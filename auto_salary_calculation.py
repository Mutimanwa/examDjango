#!/usr/bin/env python
"""
Script pour automatiser le calcul des salaires à la fin du mois
Ce script peut être exécuté via cron ou un planificateur de tâches
"""

import os
import sys
import django
from datetime import datetime, date
from pathlib import Path

# Ajouter le répertoire du projet au path Python
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_attendance_system.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from employees.models import SalaryCalculation


def should_calculate_salaries():
    """
    Détermine si les salaires doivent être calculés
    - Le 1er de chaque mois pour le mois précédent
    - Ou si c'est la fin du mois (derniers jours)
    """
    now = timezone.now()
    today = now.date()
    
    # Vérifier si c'est le 1er du mois
    if today.day == 1:
        return True, "Premier du mois - calcul du mois précédent"
    
    # Vérifier si c'est la fin du mois (derniers 3 jours)
    if today.day >= 28:  # Approximatif pour tous les mois
        return True, "Fin du mois - calcul du mois en cours"
    
    return False, "Pas encore le moment de calculer"


def main():
    """Fonction principale"""
    print("🤖 Calcul Automatique des Salaires")
    print("=" * 50)
    print(f"📅 Date/Heure: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Vérifier si le calcul est nécessaire
    should_calc, reason = should_calculate_salaries()
    
    if not should_calc:
        print(f"⏳ {reason}")
        return
    
    print(f"✅ {reason}")
    
    # Déterminer le mois à calculer
    now = timezone.now()
    if now.day == 1:
        # Premier du mois : calculer le mois précédent
        if now.month == 1:
            month = 12
            year = now.year - 1
        else:
            month = now.month - 1
            year = now.year
    else:
        # Fin du mois : calculer le mois en cours
        month = now.month
        year = now.year
    
    print(f"📊 Calcul des salaires pour {month}/{year}")
    
    # Vérifier si déjà calculé
    existing = SalaryCalculation.objects.filter(month=month, year=year).count()
    if existing > 0:
        print(f"⚠️  Les salaires pour {month}/{year} ont déjà été calculés ({existing} employés)")
        print("💡 Utilisez --force pour recalculer si nécessaire")
        return
    
    try:
        # Exécuter la commande de calcul
        call_command(
            'calculate_monthly_salaries',
            month=month,
            year=year,
            verbosity=2
        )
        print("🎉 Calcul automatique terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul automatique: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
