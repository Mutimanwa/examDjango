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
from io import BytesIO

from .models import Employee, Department, SalaryCalculation
from attendance.models import Attendance, LeaveRequest

@login_required
def add_employe(request):
    """ Ajout d'un employe """
@login_required
def profile(request):
    """Profil de l'employé"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if request.method == 'POST':
        # Mise à jour du profil
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        employee.phone_number = request.POST.get('phone_number', employee.phone_number)
        employee.address = request.POST.get('address', employee.address)
        employee.save()
        
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('employees:profile')
    
    return render(request, 'employees/profile.html', {'employee': employee})


@login_required
def payslips(request):
    """Liste des bulletins de paie de l'employé"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    payslips = SalaryCalculation.objects.filter(employee=employee).order_by('-year', '-month')
    
    # Filtrage par année si spécifié
    year_filter = request.GET.get('year')
    if year_filter:
        payslips = payslips.filter(year=int(year_filter))
    
    context = {
        'payslips': payslips,
        'available_years': SalaryCalculation.objects.filter(
            employee=employee
        ).values_list('year', flat=True).distinct().order_by('-year'),
        'selected_year': year_filter,
    }
    
    return render(request, 'employees/payslips.html', context)


@login_required
def download_payslip(request, year, month):
    """Téléchargement du bulletin de paie en PDF (version simplifiée)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    try:
        payslip = SalaryCalculation.objects.get(
            employee=employee,
            year=year,
            month=month
        )
    except SalaryCalculation.DoesNotExist:
        messages.error(request, "Bulletin de paie non trouvé.")
        return redirect('employees:payslips')
    
    # Génération d'un fichier texte simple (en attendant reportlab)
    content = f"""
BULLETIN DE PAIE
================

Nom: {employee.user.first_name} {employee.user.last_name}
ID Employé: {employee.employee_id}
Département: {employee.department.name}
Période: {calendar.month_name[month]} {year}

DÉTAILS DU SALAIRE
==================
Salaire de base: {payslip.base_salary:,.2f} €
Pourcentage de présence: {payslip.attendance_percentage}%
Déduction (si < 75%): {payslip.deduction_amount:,.2f} €

SALAIRE NET: {payslip.net_salary:,.2f} €

Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}
    """
    
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="payslip_{employee.employee_id}_{year}_{month:02d}.txt"'
    
    return response


def get_monthly_attendance_stats():
    """Statistiques mensuelles de présence pour HR"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    attendances = Attendance.objects.filter(
        date__year=current_year,
        date__month=current_month
    )
    
    total_days = attendances.count()
    present_days = attendances.filter(status='PRESENT').count()
    absent_days = attendances.filter(status='ABSENT').count()
    half_days = attendances.filter(status='HALF_DAY').count()
    leave_days = attendances.filter(status='LEAVE').count()
    
    return {
        'total': total_days,
        'present': present_days,
        'absent': absent_days,
        'half_day': half_days,
        'leave': leave_days,
        'attendance_rate': round((present_days + half_days * 0.5) / total_days * 100, 2) if total_days > 0 else 0,
    }


def get_department_stats(department):
    """Statistiques du département pour Manager"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    department_employees = Employee.objects.filter(department=department, is_active=True)
    attendances = Attendance.objects.filter(
        employee__department=department,
        date__year=current_year,
        date__month=current_month
    )
    
    return {
        'total_employees': department_employees.count(),
        'total_attendances': attendances.count(),
        'present_days': attendances.filter(status='PRESENT').count(),
        'absent_days': attendances.filter(status='ABSENT').count(),
    }
