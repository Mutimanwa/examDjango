#!/usr/bin/env python
"""
Script de test pour simuler le calcul automatique des salaires
"""

import os
import sys
import django
from datetime import datetime, date
from pathlib import Path

# Configuration Django
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_attendance_system.settings')
django.setup()

from django.core.management import call_command
from employees.models import SalaryCalculation, Employee
from attendance.models import Attendance


def test_automatic_calculation():
    """Test du calcul automatique des salaires"""
    print("🧪 Test du Calcul Automatique des Salaires")
    print("=" * 60)
    
    # Afficher les données existantes
    print("\n📊 Données existantes :")
    print(f"   👥 Employés actifs : {Employee.objects.filter(is_active=True).count()}")
    print(f"   📅 Présences : {Attendance.objects.count()}")
    print(f"   💰 Calculs de salaires : {SalaryCalculation.objects.count()}")
    
    # Test 1: Calcul pour septembre 2025
    print("\n🔬 Test 1: Calcul pour septembre 2025")
    print("-" * 40)
    try:
        call_command(
            'calculate_monthly_salaries',
            month=9,
            year=2025,
            force=True,
            verbosity=2
        )
        print("✅ Test 1 réussi!")
    except Exception as e:
        print(f"❌ Test 1 échoué: {e}")
    
    # Test 2: Vérification des résultats
    print("\n🔍 Test 2: Vérification des résultats")
    print("-" * 40)
    calculations = SalaryCalculation.objects.filter(month=9, year=2025)
    
    print(f"   📊 Calculs trouvés : {calculations.count()}")
    
    for calc in calculations:
        status = "✅" if calc.attendance_percentage >= 75 else "⚠️"
        print(f"   {status} {calc.employee.user.get_full_name()}: "
              f"{calc.attendance_percentage}% → {calc.net_salary:,.2f}€")
    
    # Test 3: Simulation de l'automatisation
    print("\n🤖 Test 3: Simulation de l'automatisation")
    print("-" * 40)
    
    # Simuler le script d'automatisation
    from auto_salary_calculation import should_calculate_salaries, main
    
    should_calc, reason = should_calculate_salaries()
    print(f"   📅 Déclenchement automatique : {should_calc}")
    print(f"   💭 Raison : {reason}")
    
    if should_calc:
        print("   🚀 Exécution du calcul automatique...")
        main()
    else:
        print("   ⏳ Pas encore le moment de calculer")
    
    # Test 4: Statistiques finales
    print("\n📈 Test 4: Statistiques finales")
    print("-" * 40)
    
    total_base = sum(sc.base_salary for sc in calculations)
    total_deductions = sum(sc.deduction_amount for sc in calculations)
    total_net = sum(sc.net_salary for sc in calculations)
    
    print(f"   💰 Salaire de base total : {total_base:,.2f}€")
    print(f"   💸 Déductions totales : {total_deductions:,.2f}€")
    print(f"   💵 Salaire net total : {total_net:,.2f}€")
    
    # Test 5: Vérification des règles
    print("\n📋 Test 5: Vérification des règles")
    print("-" * 40)
    
    deductions_applied = calculations.filter(deduction_amount__gt=0).count()
    no_deductions = calculations.filter(deduction_amount=0).count()
    
    print(f"   ✅ Employés sans déduction : {no_deductions}")
    print(f"   ⚠️  Employés avec déduction : {deductions_applied}")
    
    # Vérifier la règle des 75%
    for calc in calculations:
        if calc.attendance_percentage < 75 and calc.deduction_amount == 0:
            print(f"   ❌ ERREUR: {calc.employee.user.get_full_name()} "
                  f"a {calc.attendance_percentage}% mais pas de déduction!")
        elif calc.attendance_percentage >= 75 and calc.deduction_amount > 0:
            print(f"   ❌ ERREUR: {calc.employee.user.get_full_name()} "
                  f"a {calc.attendance_percentage}% mais a une déduction!")
    
    print("\n🎉 Tests terminés!")
    print("=" * 60)


if __name__ == '__main__':
    test_automatic_calculation()
