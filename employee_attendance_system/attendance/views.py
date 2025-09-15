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

from employees.models import Employee, Department, SalaryCalculation
from .models import Attendance, LeaveRequest


@login_required
def attendance_list(request):
    """Liste des présences (HR/Admin et Managers)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role not in ['HR', 'MANAGER']:
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    attendances = Attendance.objects.select_related('employee__user', 'employee__department').order_by('-date')
    
    # Filtres
    department_filter = request.GET.get('department')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_filter = request.GET.get('employee')
    
    if employee.role == 'MANAGER':
        # Managers ne voient que leur département
        attendances = attendances.filter(employee__department=employee.department)
    
    if department_filter:
        attendances = attendances.filter(employee__department_id=department_filter)
    if status_filter:
        attendances = attendances.filter(status=status_filter)
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if employee_filter:
        attendances = attendances.filter(employee_id=employee_filter)
    
    # Départements disponibles pour les filtres
    if employee.role == 'HR':
        departments = Department.objects.all()
        employees = Employee.objects.filter(is_active=True)
    else:
        departments = [employee.department]
        employees = Employee.objects.filter(department=employee.department, is_active=True)
    
    context = {
        'attendances': attendances,
        'departments': departments,
        'employees': employees,
        'status_choices': Attendance.STATUS_CHOICES,
        'filters': {
            'department': department_filter,
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'employee': employee_filter,
        }
    }
    
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def mark_attendance(request):
    """Marquer la présence (HR/Admin et Managers)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role not in ['HR', 'MANAGER']:
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date')
        status = request.POST.get('status')
        check_in_time = request.POST.get('check_in_time')
        check_out_time = request.POST.get('check_out_time')
        notes = request.POST.get('notes', '')
        
        try:
            target_employee = Employee.objects.get(id=employee_id)
            
            # Vérifier les permissions pour les managers
            if employee.role == 'MANAGER' and target_employee.department != employee.department:
                messages.error(request, "Vous ne pouvez marquer la présence que des employés de votre département.")
                return redirect('attendance:mark_attendance')
            
            # Créer ou mettre à jour la présence
            attendance, created = Attendance.objects.get_or_create(
                employee=target_employee,
                date=date_str,
                defaults={
                    'status': status,
                    'check_in_time': check_in_time if check_in_time else None,
                    'check_out_time': check_out_time if check_out_time else None,
                    'notes': notes,
                    'marked_by': request.user,
                }
            )
            
            if not created:
                attendance.status = status
                attendance.check_in_time = check_in_time if check_in_time else None
                attendance.check_out_time = check_out_time if check_out_time else None
                attendance.notes = notes
                attendance.marked_by = request.user
                attendance.save()
            
            action = "créée" if created else "mise à jour"
            messages.success(request, f"Présence {action} avec succès pour {target_employee.user.get_full_name()}.")
            return redirect('attendance:attendance_list')
            
        except Employee.DoesNotExist:
            messages.error(request, "Employé non trouvé.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
    
    # Employés disponibles pour marquer la présence
    if employee.role == 'HR':
        available_employees = Employee.objects.filter(is_active=True).order_by('user__last_name')
    else:
        available_employees = Employee.objects.filter(
            department=employee.department, 
            is_active=True
        ).order_by('user__last_name')
    
    context = {
        'employees': available_employees,
        'status_choices': Attendance.STATUS_CHOICES,
        'today': date.today().isoformat(),
    }
    
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def mark_employee_attendance(request, employee_id):
    """Marquer la présence d'un employé spécifique"""
    try:
        current_employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if current_employee.role not in ['HR', 'MANAGER']:
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    target_employee = get_object_or_404(Employee, id=employee_id)
    
    # Vérifier les permissions pour les managers
    if current_employee.role == 'MANAGER' and target_employee.department != current_employee.department:
        messages.error(request, "Vous ne pouvez marquer la présence que des employés de votre département.")
        return redirect('attendance:attendance_list')
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        status = request.POST.get('status')
        check_in_time = request.POST.get('check_in_time')
        check_out_time = request.POST.get('check_out_time')
        notes = request.POST.get('notes', '')
        
        try:
            attendance, created = Attendance.objects.get_or_create(
                employee=target_employee,
                date=date_str,
                defaults={
                    'status': status,
                    'check_in_time': check_in_time if check_in_time else None,
                    'check_out_time': check_out_time if check_out_time else None,
                    'notes': notes,
                    'marked_by': request.user,
                }
            )
            
            if not created:
                attendance.status = status
                attendance.check_in_time = check_in_time if check_in_time else None
                attendance.check_out_time = check_out_time if check_out_time else None
                attendance.notes = notes
                attendance.marked_by = request.user
                attendance.save()
            
            action = "créée" if created else "mise à jour"
            messages.success(request, f"Présence {action} avec succès.")
            return redirect('attendance:attendance_list')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
    
    # Récupérer les présences récentes de cet employé
    recent_attendances = Attendance.objects.filter(
        employee=target_employee
    ).order_by('-date')[:10]
    
    context = {
        'target_employee': target_employee,
        'status_choices': Attendance.STATUS_CHOICES,
        'today': date.today().isoformat(),
        'recent_attendances': recent_attendances,
    }
    
    return render(request, 'attendance/mark_employee_attendance.html', context)


@login_required
def my_attendance(request):
    """Mes présences (Employés)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')
    
    # Filtres
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status_filter:
        attendances = attendances.filter(status=status_filter)
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    
    # Statistiques personnelles
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_attendances = attendances.filter(
        date__year=current_year,
        date__month=current_month
    )
    
    present_days = monthly_attendances.filter(status='PRESENT').count()
    half_days = monthly_attendances.filter(status='HALF_DAY').count()
    absent_days = monthly_attendances.filter(status='ABSENT').count()
    leave_days = monthly_attendances.filter(status='LEAVE').count()
    
    total_working_days = present_days + half_days + absent_days + leave_days
    attendance_percentage = (present_days + (half_days * 0.5)) / total_working_days * 100 if total_working_days > 0 else 0
    
    context = {
        'attendances': attendances,
        'status_choices': Attendance.STATUS_CHOICES,
        'filters': {
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
        },
        'monthly_stats': {
            'present': present_days,
            'half_day': half_days,
            'absent': absent_days,
            'leave': leave_days,
            'percentage': round(attendance_percentage, 2),
        }
    }
    
    return render(request, 'attendance/my_attendance.html', context)


@login_required
def calculate_monthly_salary(request):
    """Calculer les salaires mensuels (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        # Calculer les salaires pour tous les employés actifs
        employees = Employee.objects.filter(is_active=True)
        calculated_count = 0
        
        for emp in employees:
            # Calculer le pourcentage de présence
            attendances = Attendance.objects.filter(
                employee=emp,
                date__year=year,
                date__month=month
            )
            
            total_days = attendances.count()
            if total_days == 0:
                continue
            
            present_days = attendances.filter(status='PRESENT').count()
            half_days = attendances.filter(status='HALF_DAY').count()
            
            attendance_percentage = (present_days + (half_days * 0.5)) / total_days * 100
            
            # Calculer les déductions
            deduction_amount = Decimal('0')
            if attendance_percentage < 75:
                deduction_amount = emp.base_salary * Decimal('0.15')
            
            net_salary = emp.base_salary - deduction_amount
            
            # Créer ou mettre à jour le calcul de salaire
            salary_calc, created = SalaryCalculation.objects.get_or_create(
                employee=emp,
                month=month,
                year=year,
                defaults={
                    'base_salary': emp.base_salary,
                    'attendance_percentage': round(attendance_percentage, 2),
                    'deduction_amount': deduction_amount,
                    'net_salary': net_salary,
                }
            )
            
            if not created:
                salary_calc.base_salary = emp.base_salary
                salary_calc.attendance_percentage = round(attendance_percentage, 2)
                salary_calc.deduction_amount = deduction_amount
                salary_calc.net_salary = net_salary
                salary_calc.save()
            
            calculated_count += 1
        
        messages.success(request, f"Salaires calculés pour {calculated_count} employés.")
        return redirect('employees:salary_report')
    
    context = {
        'current_month': datetime.now().month,
        'current_year': datetime.now().year,
    }
    
    return render(request, 'attendance/calculate_salary.html', context)


@login_required
def leave_requests(request):
    """Gestion des demandes de congé"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role == 'HR':
        # HR voit toutes les demandes
        leave_requests = LeaveRequest.objects.select_related('employee__user').order_by('-created_at')
    else:
        # Autres rôles voient seulement leurs demandes
        leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
    }
    
    return render(request, 'attendance/leave_requests.html', context)


@login_required
def request_leave(request):
    """Demander un congé"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason', '')
        
        if start_date and end_date:
            LeaveRequest.objects.create(
                employee=employee,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            messages.success(request, "Demande de congé soumise avec succès.")
            return redirect('attendance:leave_requests')
    
    return render(request, 'attendance/request_leave.html')


@login_required
def approve_leave(request, leave_id):
    """Approuver une demande de congé (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.status = 'APPROVED'
    leave_request.approved_by = request.user
    leave_request.approved_at = timezone.now()
    leave_request.save()
    
    messages.success(request, "Demande de congé approuvée.")
    return redirect('attendance:leave_requests')


@login_required
def reject_leave(request, leave_id):
    """Rejeter une demande de congé (HR/Admin uniquement)"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Profil employé non trouvé.")
        return redirect('login')
    
    if employee.role != 'HR':
        messages.error(request, "Accès non autorisé.")
        return redirect('employees:dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.status = 'REJECTED'
    leave_request.approved_by = request.user
    leave_request.approved_at = timezone.now()
    leave_request.save()
    
    messages.success(request, "Demande de congé rejetée.")
    return redirect('attendance:leave_requests')