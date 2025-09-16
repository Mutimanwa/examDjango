# Système de Gestion des Présences et Salaires

## Description
Système web complet développé avec Django pour la gestion des présences des employés et le calcul automatique des salaires avec déductions basées sur l'assiduité.

## Fonctionnalités Principales

### 🔐 Authentification et Autorisation
- **3 rôles distincts** :
  - **HR/Admin** : Accès complet à toutes les données
  - **Managers** : Gestion des présences de leur département + rapports salariaux
  - **Employees** : Vue limitée à leurs propres données

### 📊 Gestion des Présences
- Marquage quotidien des présences (Présent, Absent, Demi-journée, Congé)
- Suivi des heures d'arrivée et de départ
- Historique complet des présences
- Filtres avancés par département, employé, statut, période

### 💰 Calcul Automatique des Salaires
- Calcul basé sur le taux de présence mensuel
- **Règle de déduction** : Si présence < 75% → déduction de 15% du salaire de base
- Génération de bulletins de paie téléchargeables
- Rapports de salaires détaillés

### 📈 Rapports et Tableaux de Bord
- **Rapport de présences** : Liste filtrable de toutes les présences
- **Rapport de salaires** : Rapport mensuel par employé
- **Tableaux de bord adaptés** selon le rôle de l'utilisateur
- Export des données en CSV

### 👤 Auto-service Employé
- Consultation de l'historique des présences personnelles
- Téléchargement des bulletins de paie
- Modification du profil personnel
- Alertes en cas de taux de présence insuffisant

## Technologies Utilisées

- **Backend** : Django 4.2
- **Base de données** : SQLite (développement)
- **Frontend** : Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentification** : Django Auth System
- **Interface** : Templates Django avec design responsive

## Installation et Configuration

### Prérequis
- Python 3.8+
- Django 4.2+
- pip

### Installation
```bash
# Cloner le projet
git clone <repository-url>
cd employee_attendance_system

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Créer des données de test (optionnel)
python create_test_data.py

# Démarrer le serveur
python manage.py runserver
```

### Accès au système
- URL : http://localhost:8000
- Interface d'administration : http://localhost:8000/admin

## Comptes de Test

Les données de test créent automatiquement les comptes suivants :

| Rôle | Nom d'utilisateur | Mot de passe | Description |
|------|------------------|--------------|-------------|
| HR/Admin | hr_admin | password123 | Marie Dupont - Accès complet |
| Manager | manager_it | password123 | Jean Martin - Gestion IT |
| Employé | dev1 | password123 | Sophie Bernard - Développeuse |
| Employé | dev2 | password123 | Pierre Leroy - Développeur |
| Employé | accountant | password123 | Claire Moreau - Comptable |
| Employé | sales_rep | password123 | Thomas Petit - Commercial |

## Structure du Projet

```
employee_attendance_system/
├── employees/                 # Application des employés
│   ├── models.py             # Modèles Employee, Department, SalaryCalculation
│   ├── views.py              # Vues principales
│   ├── urls.py               # URLs des employés
│   └── templates/            # Templates des employés
├── attendance/                # Application des présences
│   ├── models.py             # Modèles Attendance, LeaveRequest
│   ├── views.py              # Vues des présences
│   ├── urls.py               # URLs des présences
│   └── templates/            # Templates des présences
├── templates/                 # Templates de base
│   ├── base/                 # Template de base
│   └── registration/         # Templates d'authentification
├── static/                   # Fichiers statiques
│   ├── css/                  # Styles CSS
│   └── js/                   # JavaScript
├── create_test_data.py       # Script de données de test
└── requirements.txt          # Dépendances Python
```

## Modèles de Données

### Employee
- Informations personnelles et professionnelles
- Liaison avec User Django
- Rôle (HR, MANAGER, EMPLOYEE)
- Salaire de base et département

### Attendance
- Enregistrement quotidien des présences
- Statuts : PRESENT, ABSENT, HALF_DAY, LEAVE
- Heures d'arrivée et de départ
- Notes et responsable du marquage

### SalaryCalculation
- Calculs mensuels des salaires
- Taux de présence et déductions
- Salaire net final
- Statut de paiement

## Règles Métier

### Calcul des Présences
- **Présent** : 1 jour complet
- **Demi-journée** : 0.5 jour
- **Absent** : 0 jour
- **Congé** : 0 jour

### Déductions Salariales
- Si taux de présence < 75% → déduction de 15%
- Salaire net = Salaire de base - Déduction

## Fonctionnalités Avancées

### Filtres et Recherche
- Filtrage par département, employé, statut, période
- Recherche en temps réel
- Export des données en CSV

### Interface Responsive
- Design adaptatif pour mobile et desktop
- Navigation intuitive selon le rôle
- Animations et transitions fluides

### Sécurité
- Authentification obligatoire
- Contrôle d'accès basé sur les rôles
- Protection CSRF
- Validation des données

## Déploiement

### Production
1. Configurer une base de données PostgreSQL/MySQL
2. Installer les dépendances de production
3. Configurer les variables d'environnement
4. Collecter les fichiers statiques
5. Configurer un serveur web (Nginx + Gunicorn)

### Variables d'Environnement
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est développé dans le cadre d'un examen final pour le cours de programmation Python de l'équipe BIU.

## Équipe de Développement

- **Mutimanwa**

## Support

Pour toute question ou problème, contactez l'équipe de développement ou créez une issue sur le repository GitHub.

---

*Développé avec ❤️ par l'équipe Mutimanwa de BIU*
