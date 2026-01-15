"""
Commande Django pour calculer automatiquement les salaires mensuels
Usage: python manage.py calculate_monthly_salaries [--month MONTH] [--year YEAR]
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
from employees.models import Employee, SalaryCalculation
from attendance.models import Attendance


class Command(BaseCommand):
    help = 'Calcule automatiquement les salaires mensuels pour tous les employés'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Mois à calculer (1-12). Par défaut: mois précédent',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Année à calculer. Par défaut: année actuelle',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recalculer même si déjà calculé',
        )

    def handle(self, *args, **options):
        # Déterminer le mois et l'année à calculer
        now = timezone.now()
        if options['month']:
            month = options['month']
        else:
            # Par défaut, calculer le mois précédent
            if now.month == 1:
                month = 12
            else:
                month = now.month - 1
        
        if options['year']:
            year = options['year']
        else:
            # Si on est en janvier et qu'on calcule décembre, prendre l'année précédente
            if now.month == 1 and month == 12:
                year = now.year - 1
            else:
                year = now.year

        self.stdout.write(
            self.style.SUCCESS(f'🔄 Calcul des salaires pour {month}/{year}...')
        )

        # Vérifier si déjà calculé
        if not options['force']:
            existing_calculations = SalaryCalculation.objects.filter(
                month=month, year=year
            ).count()
            if existing_calculations > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Les salaires pour {month}/{year} ont déjà été calculés '
                        f'({existing_calculations} employés). Utilisez --force pour recalculer.'
                    )
                )
                return

        # Calculer les salaires pour tous les employés actifs
        employees = Employee.objects.filter(is_active=True)
        calculated_count = 0
        error_count = 0

        for emp in employees:
            try:
                # Calculer le pourcentage de présence
                attendances = Attendance.objects.filter(
                    employee=emp,
                    date__year=year,
                    date__month=month
                )
                
                total_days = attendances.count()
                if total_days == 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Aucune présence trouvée pour {emp.user.get_full_name()} en {month}/{year}'
                        )
                    )
                    continue
                
                present_days = attendances.filter(status='PRESENT').count()
                half_days = attendances.filter(status='HALF_DAY').count()
                
                attendance_percentage = (present_days + (half_days * 0.5)) / total_days * 100
                
                # Calculer les déductions (15% si < 75% de présence)
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
                
                if not created and options['force']:
                    # Mettre à jour si recalcul forcé
                    salary_calc.base_salary = emp.base_salary
                    salary_calc.attendance_percentage = round(attendance_percentage, 2)
                    salary_calc.deduction_amount = deduction_amount
                    salary_calc.net_salary = net_salary
                    salary_calc.save()
                
                calculated_count += 1
                
                # Afficher le statut
                status_icon = "✅" if attendance_percentage >= 75 else "⚠️"
                self.stdout.write(
                    f'{status_icon} {emp.user.get_full_name()}: '
                    f'{attendance_percentage:.1f}% présence, '
                    f'Salaire net: {net_salary:,.2f}€'
                )
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erreur pour {emp.user.get_full_name()}: {str(e)}'
                    )
                )

        # Résumé final
        self.stdout.write('\n' + '='*50)
        if calculated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Salaires calculés avec succès pour {calculated_count} employés'
                )
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'❌ {error_count} erreurs rencontrées')
            )
        
        # Statistiques globales
        total_base = sum(
            sc.base_salary for sc in SalaryCalculation.objects.filter(
                month=month, year=year
            )
        )
        total_deductions = sum(
            sc.deduction_amount for sc in SalaryCalculation.objects.filter(
                month=month, year=year
            )
        )
        total_net = sum(
            sc.net_salary for sc in SalaryCalculation.objects.filter(
                month=month, year=year
            )
        )
        
        self.stdout.write(f'💰 Salaire de base total: {total_base:,.2f}€')
        self.stdout.write(f'💸 Déductions totales: {total_deductions:,.2f}€')
        self.stdout.write(f'💵 Salaire net total: {total_net:,.2f}€')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Calcul terminé pour {month}/{year}!'
            )
        )
