from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Demi-journée'),
        ('LEAVE', 'Congé'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendances')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee__user__last_name']
    
    @property
    def is_present(self):
        return self.status == 'PRESENT'
    
    @property
    def is_half_day(self):
        return self.status == 'HALF_DAY'
    
    @property
    def is_absent(self):
        return self.status == 'ABSENT'
    
    @property
    def is_leave(self):
        return self.status == 'LEAVE'


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date}"
    
    class Meta:
        verbose_name = "Demande de Congé"
        verbose_name_plural = "Demandes de Congés"
        ordering = ['-created_at']