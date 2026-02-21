# lakoli_admin_api
#  School Management System - Backend API

Système de gestion scolaire complet développé avec Django & Django REST Framework pour gérer plus de 900 élèves.

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Fonctionnalités](#fonctionnalités)
3. [Stack Technique](#stack-technique)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Documentation API](#documentation-api)
7. [Tests](#tests)
8. [Déploiement](#déploiement)
9. [Contribution](#contribution)

---

## Vue d'ensemble

Application backend complète pour la gestion d'établissements scolaires incluant :
- Gestion des utilisateurs (élèves, enseignants, parents, administrateurs)
- Système pédagogique (notes, emplois du temps, présences, bulletins)
- Gestion administrative (années scolaires, inscriptions, salles)
- Module financier (frais, factures, paiements)


**Équipe Backend** : Peve Beavogui  
**Équipe Frontend** : Ahmed Kipertino  
**Date de début** : Février 2026

---

## Fonctionnalités

### Gestion des Utilisateurs
- Système de rôles multi-niveaux (Admin, Enseignant, Élève, Parent, Comptable)
- Authentification JWT sécurisée
- Profils personnalisés par rôle
- Gestion des permissions granulaires

### Module Pédagogique
- Gestion des classes et matières
- Emplois du temps dynamiques
- Saisie et consultation des notes
- Suivi des présences/absences avec notifications
- Génération automatique de bulletins (PDF)
- Cahier de texte numérique
- Gestion des devoirs

###  Administration
- Gestion des années scolaires
- Processus d'inscription
- Gestion des salles et équipements
- Personnel non-enseignant

### Finances
- Définition des frais scolaires
- Génération de factures
- Suivi des paiements (espèces, mobile money, etc.)
- Rappels automatiques de paiement
- Rapports financiers (Excel/PDF)

### Communication
- Messagerie interne
- Système de notifications
- Actualités de l'école
- Notifications email/SMS

### Bibliothèque
- Stockage de documents pédagogiques
- Gestion des devoirs
- Cahier de texte
- Versioning des documents

---

## Stack Technique

| Technologie | Version | Usage |
|-------------|---------|-------|
| **Python** | 3.11+ | Langage principal |
| **Django** | 5.0+ | Framework web |
| **DRF** | 3.14+ | API REST |
| **PostgreSQL** | 15+ | Base de données |
| **Redis** | 7.0+ | Cache & message broker |
| **Celery** | 5.3+ | Tâches asynchrones |
| **Gunicorn** | 21+ | Serveur WSGI |
| **Nginx** | 1.24+ | Reverse proxy |
| **Docker** | - | Containerisation |
| **AWS S3** | - | Stockage fichiers |

---

## Installation

### Prérequis

```bash
- Python 3.11+
- PostgreSQL 15+(sqlite pour debuter)
- Redis 7+
- Git
```
### Installation Locale (Développement)
````bash
# 1. Cloner le repository
git clone https://github.com/margueritebea/lakoli_admin_api.git
# ou via SSH
git clone git@github.com:margueritebea/lakoli_admin_api.git

cd lakoli_admin_api
````
````bash
# 2. Installer les dépendances avec Make
make setup        # Linux / Mac
make setupwin     # Windows
````
````bash
# 3. Activer l'environnement virtuel
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
````
````bash
# 4. Créer le fichier .env
cp .env.example .env
# Editer .env et renseigner vos variables (base de données, secret key, etc.)
````
````bash
# 5. Base de données
# Par défaut SQLite est utilisé, aucune configuration nécessaire.
# Pour utiliser PostgreSQL / MySQL / MariaDB,
# modifier DATABASE_URL dans votre fichier .env
````
````bash
# 6. Appliquer les migrations
make migrate        # Linux / Mac
make migratewin     # Windows
````
````bash
# 7. Créer un superutilisateur
make createsuperuser        # Linux / Mac
make createsuperuserwin     # Windows
````
````bash
# 8. Charger des données de test (optionnel — non disponible pour le moment)
# python scripts/seed_data.py
````
````bash
# 9. Démarrer le serveur
make run        # Linux / Mac
make runwin     # Windows
````

> Le serveur sera accessible sur **http://127.0.0.1:8000**

> Pour afficher toutes les commandes Make disponibles : `make help`

### Démarrer Services Externes

```bash
# Terminal 2 - Redis
redis-server

# Terminal 3 - Celery Worker
celery -A config worker -l info

# Terminal 4 - Celery Beat (tâches planifiées)
celery -A config beat -l info
```


---

## Configuration

### Variables d'Environnement (.env)

```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/school_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Storage (Production)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Sentry (Monitoring - Production)
SENTRY_DSN=
```

---

## 📖 Documentation API

### Endpoints Principaux

#### Authentification
```
POST   /api/auth/token/          # Obtenir token JWT
POST   /api/auth/token/refresh/  # Rafraîchir token
```

#### Utilisateurs
```
GET    /api/v1/users/           # Liste utilisateurs
POST   /api/v1/users/           # Créer utilisateur
GET    /api/v1/users/{id}/      # Détails utilisateur
GET    /api/v1/users/me/        # Utilisateur connecté
POST   /api/v1/users/{id}/change_password/
```

#### Élèves
```
GET    /api/v1/students/                  # Liste élèves
GET    /api/v1/students/{id}/             # Détails élève
GET    /api/v1/students/by_classe/        # Élèves par classe
GET    /api/v1/students/{id}/bulletin_history/
```

#### Classes
```
GET    /api/v1/classes/                 # Liste classes
GET    /api/v1/classes/{id}/emploi_du_temps/
GET    /api/v1/classes/{id}/eleves/
GET    /api/v1/classes/{id}/statistiques/
```

#### Notes
```
GET    /api/v1/notes/                   # Liste notes
POST   /api/v1/notes/                   # Créer note
POST   /api/v1/notes/saisie_multiple/   # Saisie multiple
GET    /api/v1/notes/by_eleve_periode/
```

#### Présences
```
GET    /api/v1/presences/               # Liste présences
POST   /api/v1/presences/saisie_classe/ # Saisie classe entière
```

#### Finances
```
GET    /api/v1/factures/                # Liste factures
POST   /api/v1/factures/{id}/generer_pdf/
GET    /api/v1/paiements/               # Liste paiements
POST   /api/v1/paiements/{id}/valider/
```

### Documentation Interactive

Une fois le serveur démarré, accédez à :
- **Swagger UI** : http://localhost:8000/api/schema/swagger-ui/
- **ReDoc** : http://localhost:8000/api/schema/redoc/
- **Admin Django** : http://localhost:8000/lakoli-su-admin/

---


---

##  Contribution

### Workflow Git

```bash
# 1. Créer branche feature
git checkout -b feature/nom-fonctionnalite

# 2. Développer et commiter
git add .
git commit -m "feat: description de la fonctionnalité"

# 3. Pousser vers GitHub
git push origin feature/nom-fonctionnalite

# 4. Créer Pull Request sur GitHub
```

### Convention de Commits

```
feat: Nouvelle fonctionnalité
fix: Correction de bug
docs: Documentation
style: Formatage code
refactor: Refactoring
test: Tests
chore: Tâches maintenance
```

---

## Licence

Copyright © 2026 - Tous droits réservés

---

## 📞 Contact

**Backend Developer** : Peve Beavogui  
**Frontend Developer** : Ahmed Kipertino  

**Email** : 
**Website** : 

---

## Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery](https://docs.celeryproject.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)

---

** N'oubliez pas de mettre une étoile si ce projet vous aide !**

