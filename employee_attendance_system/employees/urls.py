from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/<int:year>/<int:month>/', views.download_payslip, name='download_payslip'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/salary/', views.salary_report, name='salary_report'),
    path('manage/employees/', views.manage_employees, name='manage_employees'),
    path('manage/departments/', views.manage_departments, name='manage_departments'),
]
