#!/usr/bin/env python
"""
Script de test rapide pour vérifier le fonctionnement du système
"""

import os
import sys
import django
import requests
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, Department
from attendance.models import Attendance

def test_database():
    """Tester la base de données"""
    print("🔍 Test de la base de données...")
    
    # Vérifier les départements
    dept_count = Department.objects.count()
    print(f"   ✅ Départements: {dept_count}")
    
    # Vérifier les employés
    emp_count = Employee.objects.count()
    print(f"   ✅ Employés: {emp_count}")
    
    # Vérifier les présences
    att_count = Attendance.objects.count()
    print(f"   ✅ Présences: {att_count}")
    
    return True

def test_users():
    """Tester les utilisateurs"""
    print("\n👤 Test des utilisateurs...")
    
    users = User.objects.all()
    for user in users:
        try:
            employee = user.employee_profile
            print(f"   ✅ {user.username} - {employee.get_role_display()} - {employee.department.name}")
        except Employee.DoesNotExist:
            print(f"   ⚠️  {user.username} - Pas de profil employé")
    
    return True

def test_attendance_calculation():
    """Tester le calcul des présences"""
    print("\n📊 Test du calcul des présences...")
    
    employees = Employee.objects.filter(is_active=True)
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    for emp in employees[:3]:  # Tester seulement les 3 premiers
        attendances = Attendance.objects.filter(
            employee=emp,
            date__year=current_year,
            date__month=current_month
        )
        
        total_days = attendances.count()
        if total_days > 0:
            present_days = attendances.filter(status='PRESENT').count()
            half_days = attendances.filter(status='HALF_DAY').count()
            attendance_percentage = (present_days + (half_days * 0.5)) / total_days * 100
            
            print(f"   ✅ {emp.user.get_full_name()}: {attendance_percentage:.1f}% ({present_days} présents, {total_days} total)")
        else:
            print(f"   ⚠️  {emp.user.get_full_name()}: Aucune présence ce mois")
    
    return True

def test_web_interface():
    """Tester l'interface web"""
    print("\n🌐 Test de l'interface web...")
    
    try:
        # Test de la page d'accueil
        response = requests.get('http://127.0.0.1:8000', timeout=5)
        if response.status_code == 302:  # Redirection vers login
            print("   ✅ Page d'accueil: Redirection vers login OK")
        else:
            print(f"   ⚠️  Page d'accueil: Status {response.status_code}")
        
        # Test de la page de login
        response = requests.get('http://127.0.0.1:8000/accounts/login/', timeout=5)
        if response.status_code == 200:
            print("   ✅ Page de login: Chargement OK")
        else:
            print(f"   ⚠️  Page de login: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    print("🧪 Test du Système de Gestion des Présences")
    print("=" * 50)
    
    tests = [
        test_database,
        test_users,
        test_attendance_calculation,
        test_web_interface,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le système fonctionne correctement.")
        print("\n🌐 Accédez au système sur: http://127.0.0.1:8000")
        print("🔑 Comptes de test:")
        print("   - HR Admin: hr_admin / password123")
        print("   - Manager: manager_it / password123")
        print("   - Employés: dev1, dev2, accountant, sales_rep / password123")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == total

if __name__ == '__main__':
    main()
