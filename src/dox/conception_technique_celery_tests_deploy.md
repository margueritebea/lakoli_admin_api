# Documentation Technique Backend - Celery, Tests & Déploiement

## 7. Tâches Asynchrones avec Celery

### 7.1 Configuration Celery

```python
# config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('school_management')

# Charger la configuration depuis Django settings avec namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks dans tous les fichiers tasks.py des apps
app.autodiscover_tasks()

# Configuration des tâches périodiques (Celery Beat)
app.conf.beat_schedule = {
    # Rappels de paiement quotidiens à 9h
    'envoyer-rappels-paiement': {
        'task': 'apps.finances.tasks.envoyer_rappels_paiement',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Génération bulletins automatique fin de trimestre
    'generer-bulletins-trimestriels': {
        'task': 'apps.pedagogie.tasks.generer_bulletins_periode',
        'schedule': crontab(day_of_month=15, hour=0, minute=0),  # Le 15 de chaque mois
    },
    
    # Notification absences quotidienne à 17h
    'notifier-absences-jour': {
        'task': 'apps.pedagogie.tasks.notifier_absences_quotidiennes',
        'schedule': crontab(hour=17, minute=0),
    },
    
    # Backup base de données quotidien à 2h du matin
    'backup-database': {
        'task': 'core.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    """Tâche de debug"""
    print(f'Request: {self.request!r}')
```

```python
# config/settings/base.py

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Conakry'

# Retry configuration
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Task time limits (30 minutes)
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
```

### 7.2 Tâches Celery par App

```python
# apps/pedagogie/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Bulletin, Presence
from apps.communication.models import Notification

@shared_task(bind=True, max_retries=3)
def generer_bulletin_pdf(self, bulletin_id):
    """
    Génère le PDF d'un bulletin
    """
    try:
        bulletin = Bulletin.objects.get(id=bulletin_id)
        
        # Import tardif pour éviter problèmes de circular import
        from apps.pedagogie.utils import BulletinPDFGenerator
        
        generator = BulletinPDFGenerator(bulletin)
        pdf_file = generator.generate()
        
        # Sauvegarder le fichier
        bulletin.fichier_pdf = pdf_file
        bulletin.save()
        
        # Notifier l'élève et les parents
        Notification.objects.create(
            utilisateur=bulletin.eleve.user,
            type_notification=Notification.TypeNotificationChoices.BULLETIN,
            titre="Bulletin disponible",
            message=f"Votre bulletin du {bulletin.get_periode_display()} est disponible.",
            lien_url=f"/bulletins/{bulletin.id}",
            envoyer_par_email=True
        )
        
        return {
            'status': 'success',
            'bulletin_id': bulletin_id,
            'pdf_path': bulletin.fichier_pdf.url
        }
        
    except Bulletin.DoesNotExist:
        return {'status': 'error', 'message': 'Bulletin introuvable'}
    except Exception as exc:
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def generer_bulletins_periode(periode, annee_scolaire_id):
    """
    Génère tous les bulletins pour une période donnée
    """
    from apps.administration.models import AnneeScolaire
    from apps.authentication.models import EleveProfile
    
    annee = AnneeScolaire.objects.get(id=annee_scolaire_id)
    eleves = EleveProfile.objects.filter(classe_actuelle__annee_scolaire=annee)
    
    bulletins_crees = 0
    
    for eleve in eleves:
        # Vérifier si bulletin existe déjà
        if Bulletin.objects.filter(
            eleve=eleve,
            periode=periode,
            annee_scolaire=annee
        ).exists():
            continue
        
        # Calculer les statistiques
        from apps.pedagogie.utils import CalculateurBulletin
        calculateur = CalculateurBulletin(eleve, periode, annee)
        
        bulletin = calculateur.generer_bulletin()
        
        # Lancer génération PDF en tâche séparée
        generer_bulletin_pdf.delay(bulletin.id)
        
        bulletins_crees += 1
    
    return {
        'status': 'success',
        'bulletins_crees': bulletins_crees
    }


@shared_task
def notifier_absences_quotidiennes():
    """
    Envoie les notifications d'absences aux parents
    """
    from django.utils import timezone
    from datetime import date
    
    today = date.today()
    
    absences = Presence.objects.filter(
        date=today,
        statut__in=[Presence.StatutChoices.ABSENT, Presence.StatutChoices.RETARD],
        notification_envoyee=False
    ).select_related('eleve__user')
    
    notifications_envoyees = 0
    
    for absence in absences:
        # Trouver les parents
        parents = absence.eleve.parents.all()
        
        for parent_profile in parents:
            Notification.objects.create(
                utilisateur=parent_profile.user,
                type_notification=Notification.TypeNotificationChoices.ABSENCE if absence.statut == Presence.StatutChoices.ABSENT else Notification.TypeNotificationChoices.RETARD,
                titre=f"{'Absence' if absence.statut == Presence.StatutChoices.ABSENT else 'Retard'} signalé",
                message=f"{absence.eleve.user.get_full_name()} a été marqué comme {'absent' if absence.statut == Presence.StatutChoices.ABSENT else 'en retard'} le {absence.date}.",
                envoyer_par_email=True,
                envoyer_par_sms=True
            )
            notifications_envoyees += 1
        
        # Marquer comme notifié
        absence.notification_envoyee = True
        absence.save()
    
    return {
        'status': 'success',
        'notifications_envoyees': notifications_envoyees
    }


# apps/finances/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task(bind=True, max_retries=3)
def generer_facture_pdf(self, facture_id):
    """
    Génère le PDF d'une facture
    """
    try:
        from .models import Facture
        from .utils import FacturePDFGenerator
        
        facture = Facture.objects.get(id=facture_id)
        generator = FacturePDFGenerator(facture)
        pdf_file = generator.generate()
        
        facture.fichier_pdf = pdf_file
        facture.save()
        
        return {
            'status': 'success',
            'facture_id': facture_id,
            'pdf_path': facture.fichier_pdf.url
        }
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def envoyer_rappels_paiement():
    """
    Envoie des rappels pour les paiements en retard
    """
    from .models import Facture
    from apps.communication.models import Notification
    
    # Factures en retard (échéance dépassée)
    today = timezone.now().date()
    factures_retard = Facture.objects.filter(
        statut__in=[Facture.StatutChoices.EMISE, Facture.StatutChoices.PARTIELLEMENT_PAYEE],
        date_echeance__lt=today
    ).select_related('eleve__user')
    
    rappels_envoyes = 0
    
    for facture in factures_retard:
        # Créer notification pour élève
        Notification.objects.create(
            utilisateur=facture.eleve.user,
            type_notification=Notification.TypeNotificationChoices.RAPPEL_PAIEMENT,
            titre="Rappel de paiement",
            message=f"Votre facture {facture.numero} d'un montant de {facture.montant_restant} GNF est en retard. Échéance: {facture.date_echeance}",
            lien_url=f"/factures/{facture.id}",
            envoyer_par_email=True,
            envoyer_par_sms=True
        )
        
        # Notifier aussi les parents
        parents = facture.eleve.parents.all()
        for parent in parents:
            Notification.objects.create(
                utilisateur=parent.user,
                type_notification=Notification.TypeNotificationChoices.RAPPEL_PAIEMENT,
                titre="Rappel de paiement",
                message=f"Facture {facture.numero} pour {facture.eleve.user.get_full_name()} en retard. Montant restant: {facture.montant_restant} GNF",
                lien_url=f"/factures/{facture.id}",
                envoyer_par_email=True,
                envoyer_par_sms=True
            )
        
        rappels_envoyes += 1
    
    return {
        'status': 'success',
        'rappels_envoyes': rappels_envoyes
    }


# apps/communication/tasks.py
from celery import shared_task

@shared_task
def envoyer_notification_absence(presence_id):
    """Envoie une notification d'absence immédiate"""
    from apps.pedagogie.models import Presence
    from .models import Notification
    
    try:
        presence = Presence.objects.get(id=presence_id)
        parents = presence.eleve.parents.all()
        
        for parent in parents:
            Notification.objects.create(
                utilisateur=parent.user,
                type_notification=Notification.TypeNotificationChoices.ABSENCE,
                titre="Absence signalée",
                message=f"{presence.eleve.user.get_full_name()} a été marqué absent le {presence.date}.",
                envoyer_par_sms=True
            )
        
        return {'status': 'success'}
    except Presence.DoesNotExist:
        return {'status': 'error', 'message': 'Présence introuvable'}


@shared_task
def envoyer_email_notification(notification_id):
    """Envoie un email pour une notification"""
    from .models import Notification
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if not notification.envoyer_par_email:
            return {'status': 'skipped', 'reason': 'Email non demandé'}
        
        send_mail(
            subject=notification.titre,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.utilisateur.email],
            fail_silently=False,
        )
        
        notification.email_envoye = True
        notification.save()
        
        return {'status': 'success'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def envoyer_sms_notification(notification_id):
    """Envoie un SMS pour une notification"""
    # TODO: Intégrer Orange Money SMS API ou MTN
    pass


# core/tasks.py
from celery import shared_task

@shared_task
def backup_database():
    """Sauvegarde automatique de la base de données"""
    import subprocess
    from datetime import datetime
    from django.conf import settings
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"/backups/db_backup_{timestamp}.sql"
    
    try:
        # Utiliser pg_dump pour PostgreSQL
        subprocess.run([
            'pg_dump',
            '-h', settings.DATABASES['default']['HOST'],
            '-U', settings.DATABASES['default']['USER'],
            '-d', settings.DATABASES['default']['NAME'],
            '-f', backup_file
        ], check=True)
        
        # Optionnel: Upload vers S3
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            from .utils import upload_to_s3
            upload_to_s3(backup_file, f'backups/db_backup_{timestamp}.sql')
        
        return {'status': 'success', 'file': backup_file}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

---

## 8. Tests & Qualité du Code

### 8.1 Configuration des Tests

```python
# config/settings/test.py
from .base import *

# Base de données en mémoire pour tests rapides
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Désactiver migrations pour tests rapides
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Celery en mode eager pour tests synchrones
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend pour tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Désactiver password hashing pour tests rapides
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --nomigrations --cov=apps --cov-report=html --cov-report=term-missing
testpaths = apps tests
```

### 8.2 Exemples de Tests

```python
# apps/users/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model
from apps.authentication.models import EleveProfile

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    """Tests pour le modèle User"""
    
    def test_create_user(self):
        """Test création d'un utilisateur"""
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.RoleChoices.ELEVE
        )
        
        assert user.email == 'test@example.com'
        assert user.is_eleve is True
        assert user.check_password('testpass123')
    
    def test_user_full_name(self):
        """Test méthode get_full_name"""
        user = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='pass',
            first_name='John',
            last_name='Doe'
        )
        
        assert user.get_full_name() == 'John Doe'


# apps/users/tests/test_views.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserViewSet:
    """Tests pour les endpoints User"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def admin_user(self):
        return User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role=User.RoleChoices.ADMIN
        )
    
    def test_list_users_unauthorized(self, api_client):
        """Test accès non autorisé à la liste des users"""
        response = api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_users_authorized(self, api_client, admin_user):
        """Test accès autorisé pour admin"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_current_user(self, api_client, admin_user):
        """Test endpoint /me"""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/users/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'admin@test.com'
        assert response.data['role'] == 'ADMIN'


# apps/pedagogie/tests/test_models.py
import pytest
from apps.pedagogie.models import Classe, Matiere, Note
from apps.administration.models import AnneeScolaire
from apps.authentication.models import User, EleveProfile

@pytest.mark.django_db
class TestNoteModel:
    """Tests pour le modèle Note"""
    
    @pytest.fixture
    def setup_data(self):
        # Année scolaire
        annee = AnneeScolaire.objects.create(
            nom='2025-2026',
            date_debut='2025-09-01',
            date_fin='2026-06-30',
            est_active=True
        )
        
        # Matière
        matiere = Matiere.objects.create(
            code='MATH',
            nom='Mathématiques',
            coefficient=3
        )
        
        # Classe
        classe = Classe.objects.create(
            niveau=Classe.NiveauChoices.SIXIEME,
            nom='6ème A',
            annee_scolaire=annee
        )
        
        # Élève
        user = User.objects.create_user(
            username='eleve1',
            email='eleve1@test.com',
            password='pass',
            role=User.RoleChoices.ELEVE
        )
        eleve = EleveProfile.objects.create(
            user=user,
            matricule='2026/001',
            classe_actuelle=classe,
            contact_urgence_nom='Parent',
            contact_urgence_phone='123456789',
            contact_urgence_relation='Père',
            date_admission='2025-09-01'
        )
        
        return {
            'annee': annee,
            'matiere': matiere,
            'classe': classe,
            'eleve': eleve
        }
    
    def test_create_note(self, setup_data):
        """Test création d'une note"""
        note = Note.objects.create(
            eleve=setup_data['eleve'],
            matiere=setup_data['matiere'],
            classe=setup_data['classe'],
            annee_scolaire=setup_data['annee'],
            type_note=Note.TypeNoteChoices.DEVOIR,
            periode=Note.PeriodeChoices.TRIMESTRE_1,
            valeur=15.5,
            sur=20,
            date_evaluation='2025-10-15'
        )
        
        assert note.valeur == 15.5
        assert note.note_sur_20 == 15.5
    
    def test_note_sur_20_conversion(self, setup_data):
        """Test conversion note sur 20"""
        note = Note.objects.create(
            eleve=setup_data['eleve'],
            matiere=setup_data['matiere'],
            classe=setup_data['classe'],
            annee_scolaire=setup_data['annee'],
            type_note=Note.TypeNoteChoices.DEVOIR,
            periode=Note.PeriodeChoices.TRIMESTRE_1,
            valeur=8,
            sur=10,
            date_evaluation='2025-10-15'
        )
        
        assert note.note_sur_20 == 16.0
```

### 8.3 Commandes de Test

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=apps --cov-report=html

# Tests d'une app spécifique
pytest apps/users/tests/

# Tests en parallèle (plus rapide)
pytest -n auto

# Tests avec output détaillé
pytest -vv

# Tests d'un fichier spécifique
pytest apps/users/tests/test_models.py

# Tests d'une classe spécifique
pytest apps/users/tests/test_models.py::TestUserModel

# Tests avec marqueurs
pytest -m slow  # Tests lents
pytest -m fast  # Tests rapides
```

---

## 9. Déploiement

### 9.1 Configuration Docker

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Créer répertoire app
WORKDIR /app

# Copier requirements
COPY requirements/production.txt requirements.txt
RUN pip install -r requirements.txt

# Copier le code
COPY . .

# Collecter fichiers statiques
RUN python manage.py collectstatic --noinput

# Créer utilisateur non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exposer port
EXPOSE 8000

# Command par défaut
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: school_db
      POSTGRES_USER: school_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U school_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - ../:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: celery -A config worker -l info
    volumes:
      - ../:/app
    env_file:
      - ../.env
    depends_on:
      - db
      - redis

  celery-beat:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: celery -A config beat -l info
    volumes:
      - ../:/app
    env_file:
      - ../.env
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

```nginx
# docker/nginx/nginx.conf
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name api.votre-ecole.com;
    
    # Redirection HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.votre-ecole.com;
    
    # SSL
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 20M;
    
    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /app/media/;
        expires 30d;
    }
    
    # Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 9.2 Commandes Docker

```bash
# Build et démarrer
docker-compose -f docker/docker-compose.yml up --build -d

# Voir les logs
docker-compose -f docker/docker-compose.yml logs -f web

# Migrations
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate

# Créer superuser
docker-compose -f docker/docker-compose.yml exec web python manage.py createsuperuser

# Collecter static files
docker-compose -f docker/docker-compose.yml exec web python manage.py collectstatic --noinput

# Arrêter
docker-compose -f docker/docker-compose.yml down

# Arrêter et supprimer volumes
docker-compose -f docker/docker-compose.yml down -v
```

### 9.3 Déploiement sur VPS (Production)

```bash
# Script de déploiement - deploy.sh
#!/bin/bash

echo "🚀 Déploiement School Management Backend"

# 1. Pull dernières modifications
git pull origin main

# 2. Build images Docker
docker-compose -f docker/docker-compose.yml build

# 3. Arrêter anciens containers
docker-compose -f docker/docker-compose.yml down

# 4. Démarrer nouveaux containers
docker-compose -f docker/docker-compose.yml up -d

# 5. Migrations
docker-compose -f docker/docker-compose.yml exec -T web python manage.py migrate --noinput

# 6. Collecter static files
docker-compose -f docker/docker-compose.yml exec -T web python manage.py collectstatic --noinput

# 7. Vérifier santé des services
sleep 10
docker-compose -f docker/docker-compose.yml ps

echo "✅ Déploiement terminé!"
```

### 9.4 Monitoring & Logs

```python
# config/settings/production.py

# Sentry pour monitoring des erreurs
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment='production',
    )

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/school_backend.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## 10. Annexes

### 10.1 Structure Finale du Projet

```
school_management/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
│
├── apps/
│   ├── users/
│   ├── pedagogie/
│   ├── administration/
│   ├── finances/
│   ├── communication/
│   └── bibliotheque/
│
├── core/
│   ├── permissions.py
│   ├── pagination.py
│   ├── exceptions.py
│   └── mixins.py
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
│
├── scripts/
│   ├── seed_data.py
│   └── backup.py
│
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

### 10.2 Checklist Pré-Production

- [ ] Variables d'environnement configurées
- [ ] Secret key fort et unique
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configuré
- [ ] Base de données PostgreSQL configurée
- [ ] Redis configuré
- [ ] Certificats SSL installés
- [ ] Backups automatiques configurés
- [ ] Monitoring (Sentry) activé
- [ ] Logs configurés
- [ ] Celery et Celery Beat fonctionnels
- [ ] Tests passent tous
- [ ] Documentation API à jour
- [ ] Nginx configuré
- [ ] Firewall configuré
- [ ] CORS configuré correctement

### 10.3 Contacts & Support

**Équipe Backend** : Peve Beavogui  
**Équipe Frontend** : Ahmed Kipertino  
**Date de début prévue** : Février 2026

---

**FIN DE LA DOCUMENTATION TECHNIQUE**
