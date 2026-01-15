#!/usr/bin/env python
"""
Script de vérification des templates pour s'assurer qu'ils existent tous
"""

import os
from pathlib import Path

def check_template_exists(template_path):
    """Vérifier si un template existe"""
    full_path = Path("templates") / template_path
    return full_path.exists()

def main():
    """Vérifier tous les templates nécessaires"""
    print("🔍 Vérification des templates...")
    print("=" * 50)
    
    # Liste des templates requis
    required_templates = [
        # Templates de base
        "base/base.html",
        "registration/login.html",
        
        # Templates des employés
        "employees/dashboard_hr.html",
        "employees/dashboard_manager.html", 
        "employees/dashboard_employee.html",
        "employees/profile.html",
        "employees/payslips.html",
        "employees/attendance_report.html",
        "employees/salary_report.html",
        "employees/manage_employees.html",
        "employees/manage_departments.html",
        
        # Templates des présences
        "attendance/attendance_list.html",
        "attendance/mark_attendance.html",
        "attendance/mark_employee_attendance.html",
        "attendance/my_attendance.html",
        "attendance/calculate_salary.html",
        "attendance/leave_requests.html",
        "attendance/request_leave.html",
    ]
    
    missing_templates = []
    existing_templates = []
    
    for template in required_templates:
        if check_template_exists(template):
            existing_templates.append(template)
            print(f"✅ {template}")
        else:
            missing_templates.append(template)
            print(f"❌ {template}")
    
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {len(existing_templates)}/{len(required_templates)} templates trouvés")
    
    if missing_templates:
        print(f"\n⚠️  Templates manquants ({len(missing_templates)}):")
        for template in missing_templates:
            print(f"   - {template}")
        return False
    else:
        print("\n🎉 Tous les templates sont présents !")
        return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
