from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.units import inch
from io import BytesIO

from .models import Employee, Department, SalaryCalculation
from attendance.models import Attendance, LeaveRequest
from .views_payslip import profile, payslips, download_payslip, get_monthly_attendance_stats, get_department_stats


@login_required
def dashboard(request):
    """Tableau de bord principal adapté au rôle de l'utilisateur"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé. Contactez l'administrateur.")
        return redirect('login')
    
    context = {
        'employee': employee,
        'current_month': datetime.now().month,
        'current_year': datetime.now().year,
    }
    
    if employee.role == 'HR':
        # Vue HR/Admin - Accès complet
        context.update({
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.count(),
            'recent_attendances': Attendance.objects.select_related('employee__user').order_by('-date')[:10],
            'pending_leaves': LeaveRequest.objects.filter(status='PENDING').count(),
            'monthly_attendance_stats': get_monthly_attendance_stats(),
        })
        return render(request, 'employees/dashboard_hr.html', context)
    
    elif employee.role == 'MANAGER':
        # Vue Manager - Département uniquement
        department_employees = Employee.objects.filter(
            department=employee.department, 
            is_active=True
        ).exclude(id=employee.id)
        
        context.update({
            'department_employees': department_employees,
            'department_attendances': Attendance.objects.filter(
                employee__department=employee.department
            ).order_by('-date')[:10],
            'department_stats': get_department_stats(employee.department),
        })
        return render(request, 'employees/dashboard_manager.html', context)
    
    else:
        # Vue Employé - Données personnelles uniquement
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Statistiques personnelles
        my_attendances = Attendance.objects.filter(
            employee=employee,
            date__year=current_year,
            date__month=current_month
        )
        
        present_days = my_attendances.filter(status='PRESENT').count()
        half_days = my_attendances.filter(status='HALF_DAY').count()
        absent_days = my_attendances.filter(status='ABSENT').count()
        leave_days = my_attendances.filter(status='LEAVE').count()
        
        total_working_days = present_days + half_days + absent_days + leave_days
        attendance_percentage = (present_days + (half_days * 0.5)) / total_working_days * 100 if total_working_days > 0 else 0
        
        context.update({
            'my_attendances': my_attendances.order_by('-date')[:10],
            'attendance_stats': {
                'present': present_days,
                'half_day': half_days,
                'absent': absent_days,
                'leave': leave_days,
                'percentage': round(attendance_percentage, 2),
            },
            'recent_payslips': SalaryCalculation.objects.filter(
                employee=employee
            ).order_by('-year', '-month')[:5],
        })
        return render(request, 'employees/dashboard_employee.html', context)


@login_required
def attendance_report(request):
    """Rapport de présences (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    attendances = Attendance.objects.select_related('employee__user', 'employee__department').order_by('-date')
    
    # Filtres
    department_filter = request.GET.get('department')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if department_filter:
        attendances = attendances.filter(employee__department_id=department_filter)
    if status_filter:
        attendances = attendances.filter(status=status_filter)
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    
    context = {
        'attendances': attendances,
        'departments': Department.objects.all(),
        'status_choices': Attendance.STATUS_CHOICES,
        'filters': {
            'department': department_filter,
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'employees/attendance_report.html', context)


@login_required
def salary_report(request):
    """Rapport de salaires (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    # Filtrage par mois/année
    month = request.GET.get('month', datetime.now().month)
    year = request.GET.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except (ValueError, TypeError):
        month = datetime.now().month
        year = datetime.now().year
    
    salary_calculations = SalaryCalculation.objects.filter(
        month=month,
        year=year
    ).select_related('employee__user', 'employee__department').order_by('employee__user__last_name')
    
    total_base_salary = sum(sc.base_salary for sc in salary_calculations)
    total_deductions = sum(sc.deduction_amount for sc in salary_calculations)
    total_net_salary = sum(sc.net_salary for sc in salary_calculations)
    
    context = {
        'salary_calculations': salary_calculations,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'totals': {
            'base_salary': total_base_salary,
            'deductions': total_deductions,
            'net_salary': total_net_salary,
        },
        'available_years': SalaryCalculation.objects.values_list('year', flat=True).distinct().order_by('-year'),
    }
    
    return render(request, 'employees/salary_report.html', context)


@login_required
def manage_employees(request):
    """Gestion des employés (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    employees = Employee.objects.select_related('user', 'department').filter(is_active=True).order_by('user__last_name')
    
    # Filtrage par département
    department_filter = request.GET.get('department')
    if department_filter:
        employees = employees.filter(department_id=department_filter)
    
    context = {
        'employees': employees,
        'departments': Department.objects.all(),
        'selected_department': department_filter,
    }
    
    return render(request, 'employees/manage_employees.html', context)


@login_required
def manage_departments(request):
    """Gestion des départements (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    departments = Department.objects.annotate(
        employee_count=Count('employees', filter=Q(employees__is_active=True))
    ).order_by('name')
    
    if request.method == 'POST':
        if 'add_department' in request.POST:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                Department.objects.create(name=name, description=description)
                messages.success(request, f"Département '{name}' créé avec succès.")
                return redirect('employees:manage_departments')
    
    context = {
        'departments': departments,
    }
    
    return render(request, 'employees/manage_departments.html', context)