from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('mark/<int:employee_id>/', views.mark_employee_attendance, name='mark_employee_attendance'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('calculate-salary/', views.calculate_monthly_salary, name='calculate_monthly_salary'),
    path('leaves/', views.leave_requests, name='leave_requests'),
    path('leaves/request/', views.request_leave, name='request_leave'),
    path('leaves/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('leaves/<int:leave_id>/reject/', views.reject_leave, name='reject_leave'),
]
