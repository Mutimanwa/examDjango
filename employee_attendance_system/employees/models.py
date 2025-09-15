from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"


class Employee(models.Model):
    ROLE_CHOICES = [
        ('HR', 'HR/Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employé'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    hire_date = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['user__last_name', 'user__first_name']


class SalaryCalculation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_calculations')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    deduction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"
    
    class Meta:
        verbose_name = "Calcul de Salaire"
        verbose_name_plural = "Calculs de Salaires"
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']