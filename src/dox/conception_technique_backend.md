# Documentation Technique Backend - Système de Gestion Scolaire
**Équipe Backend** : Peve Beavogui  
**Stack** : Django 5.0 + Django REST Framework + PostgreSQL  
**Date** : 12 Février 2026  
**Version** : 1.0

---

## Table des Matières
1. [Architecture Générale](#1-architecture-générale)
2. [Configuration Environnement](#2-configuration-environnement)
3. [Structure des Apps Django](#3-structure-des-apps-django)
4. [Modèles de Données Détaillés](#4-modèles-de-données-détaillés)
5. [API REST - Endpoints](#5-api-rest-endpoints)
6. [Authentification & Sécurité](#6-authentification--sécurité)
7. [Tâches Asynchrones](#7-tâches-asynchrones)
8. [Tests & Qualité](#8-tests--qualité)
9. [Déploiement](#9-déploiement)
10. [Annexes](#10-annexes)

---

## 1. Architecture Générale

### 1.1 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend React.js                     │
│              (Géré par Ahmed Kipertino)                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Nginx (Reverse Proxy)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Django + DRF (API Backend)                  │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐│
│  │  Users   │Pédagogie │  Admin   │ Finances │ Comms  ││
│  └──────────┴──────────┴──────────┴──────────┴────────┘│
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬──────────────┐
        ▼                         ▼              ▼
   ┌─────────┐              ┌─────────┐    ┌─────────┐
   │PostgreSQL│              │  Redis  │    │  Celery │
   │    DB    │              │  Cache  │    │ Workers │
   └─────────┘              └─────────┘    └─────────┘
```

### 1.2 Stack Technique

| Composant | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| **Framework** | Django | 5.0+ | Robuste, batteries included, ORM puissant |
| **API** | Django REST Framework | 3.14+ | Standard industrie pour APIs REST |
| **Base de données** | PostgreSQL | 15+ | Performances, ACID, 900+ élèves |
| **Cache** | Redis | 7.0+ | Performance, sessions, Celery broker |
| **Tasks asynchrones** | Celery | 5.3+ | Bulletins, emails, notifications |
| **Serveur WSGI** | Gunicorn | 21+ | Production-ready |
| **Proxy** | Nginx | 1.24+ | Reverse proxy, SSL, static files |
| **Stockage fichiers** | AWS S3 / MinIO | - | Documents, bulletins, photos |

### 1.3 Principe KISS (Keep It Simple)

Pour 900 élèves, nous privilégions :
- ✅ Architecture monolithique (pas de microservices)
- ✅ PostgreSQL seul (pas de MongoDB supplémentaire)
- ✅ Déploiement simple (VPS unique ou PaaS type Railway/Render)
- ❌ Pas de Kubernetes (overkill pour cette échelle)
- ❌ Pas de GraphQL (REST suffit largement)

---

## 2. Configuration Environnement

### 2.1 Structure du Projet

```
school_management/
├── config/                      # Configuration Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Settings communs
│   │   ├── development.py      # Dev local
│   │   ├── production.py       # Production
│   │   └── test.py             # Tests
│   ├── urls.py                 # Routes principales
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # Applications Django
│   ├── users/                  # Gestion utilisateurs
│   ├── pedagogie/              # Gestion pédagogique
│   ├── administration/         # Gestion administrative
│   ├── finances/               # Gestion financière
│   ├── communication/          # Messagerie & notifications
│   └── bibliotheque/           # Ressources pédagogiques
│
├── core/                        # Utilitaires communs
│   ├── __init__.py
│   ├── permissions.py          # Permissions personnalisées
│   ├── pagination.py           # Pagination API
│   ├── exceptions.py           # Exceptions personnalisées
│   ├── validators.py           # Validateurs réutilisables
│   └── mixins.py               # Mixins pour vues/modèles
│
├── tests/                       # Tests globaux
│   ├── integration/
│   └── e2e/
│
├── media/                       # Fichiers uploadés (dev)
├── static/                      # Fichiers statiques
├── locale/                      # Traductions (i18n)
│   ├── fr/
│   └── en/
│
├── scripts/                     # Scripts utilitaires
│   ├── seed_data.py            # Données de test
│   └── backup.py               # Sauvegarde DB
│
├── requirements/
│   ├── base.txt                # Dépendances communes
│   ├── development.txt         # Dev
│   └── production.txt          # Production
│
├── docker/                      # Configuration Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
│
├── .env.example                 # Variables d'environnement template
├── .gitignore
├── manage.py
├── pytest.ini                   # Configuration pytest
└── README.md
```

### 2.2 Variables d'Environnement (.env)

```bash
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=api.votre-ecole.com,localhost

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/school_db
DB_ENGINE=django.db.backends.postgresql
DB_NAME=school_db
DB_USER=school_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (pour notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password

# SMS (Orange Money SMS API - futur)
ORANGE_SMS_API_KEY=
ORANGE_SMS_SENDER_ID=

# Storage (AWS S3 ou compatible)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=school-media
AWS_S3_REGION_NAME=eu-west-1
AWS_S3_CUSTOM_DOMAIN=cdn.votre-ecole.com

# Sentry (monitoring erreurs - optionnel)
SENTRY_DSN=

# Internationalisation
LANGUAGE_CODE=fr
TIME_ZONE=Africa/Conakry
USE_I18N=True
USE_TZ=True

# Sécurité
CORS_ALLOWED_ORIGINS=https://votre-ecole.com,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://votre-ecole.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2.3 Installation & Démarrage Rapide

```bash
# 1. Cloner et créer environnement virtuel
git clone https://github.com/votre-org/school-backend.git
cd school-backend
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Installer dépendances
pip install -r requirements/development.txt

# 3. Configurer .env
cp .env.example .env
# Éditer .env avec vos valeurs

# 4. Créer la base de données PostgreSQL
createdb school_db
# ou via psql: CREATE DATABASE school_db;

# 5. Migrations
python manage.py makemigrations
python manage.py migrate

# 6. Créer super utilisateur
python manage.py createsuperuser

# 7. Charger données de test (optionnel)
python scripts/seed_data.py

# 8. Démarrer serveur développement
python manage.py runserver

# 9. Démarrer Redis (terminal séparé)
redis-server

# 10. Démarrer Celery worker (terminal séparé)
celery -A config worker -l info

# 11. Démarrer Celery Beat pour tâches planifiées
celery -A config beat -l info
```

---

## 3. Structure des Apps Django

### 3.1 Vue d'Ensemble des Apps

| App | Responsabilité | Modèles Principaux |
|-----|----------------|-------------------|
| **users** | Authentification, profils, rôles | User, Profile, Role, Permission |
| **pedagogie** | Classes, notes, emploi du temps | Classe, Matiere, Note, EmploiDuTemps, Presence |
| **administration** | Années scolaires, inscriptions | AnneeScolaire, Inscription, Salle, PersonnelNonEnseignant |
| **finances** | Frais, paiements, rapports | FraisScolaire, Paiement, Facture, RapportFinancier |
| **communication** | Messages, notifications | Message, Notification, Actualite |
| **bibliotheque** | Documents, ressources | Document, Categorie, CahierDeTexte, Devoir |

### 3.2 Structure Standard d'une App

```
apps/nom_app/
├── __init__.py
├── models.py                # Modèles de données
├── serializers.py           # DRF Serializers
├── views.py                 # API ViewSets
├── urls.py                  # Routes de l'app
├── admin.py                 # Interface admin Django
├── permissions.py           # Permissions spécifiques
├── filters.py               # Filtres django-filter
├── signals.py               # Signaux Django (optionnel)
├── tasks.py                 # Tâches Celery (optionnel)
├── validators.py            # Validateurs custom
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_serializers.py
│   ├── test_views.py
│   └── test_permissions.py
└── migrations/
    └── __init__.py
```

---

## 4. Modèles de Données Détaillés

### 4.1 App `users` - Gestion Utilisateurs

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec rôles multiples.
    Hérite de AbstractUser pour compatibilité avec système auth Django.
    """
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        ENSEIGNANT = 'ENSEIGNANT', _('Enseignant')
        ELEVE = 'ELEVE', _('Élève')
        PARENT = 'PARENT', _('Parent')
        COMPTABLE = 'COMPTABLE', _('Comptable')
        SURVEILLANT = 'SURVEILLANT', _('Surveillant')
    
    # Override email pour le rendre unique et obligatoire
    email = models.EmailField(_('adresse email'), unique=True)
    
    # Informations de base
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.ELEVE
    )
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    address = models.TextField(_('adresse'), blank=True)
    photo = models.ImageField(
        _('photo de profil'),
        upload_to='users/photos/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Date de naissance (important pour élèves)
    date_of_birth = models.DateField(_('date de naissance'), null=True, blank=True)
    
    # Métadonnées
    is_verified = models.BooleanField(_('compte vérifié'), default=False)
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)
    
    # Langue préférée
    preferred_language = models.CharField(
        _('langue préférée'),
        max_length=5,
        choices=[('fr', 'Français'), ('en', 'English')],
        default='fr'
    )
    
    # USERNAME_FIELD = 'email'  # Connexion par email au lieu de username
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'role']
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active', 'role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_enseignant(self):
        return self.role == self.RoleChoices.ENSEIGNANT
    
    @property
    def is_eleve(self):
        return self.role == self.RoleChoices.ELEVE
    
    @property
    def is_parent(self):
        return self.role == self.RoleChoices.PARENT
    
    @property
    def is_comptable(self):
        return self.role == self.RoleChoices.COMPTABLE


class EleveProfile(TimeStampedModel):
    """
    Profil spécifique aux élèves avec informations pédagogiques.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='eleve_profile',
        limit_choices_to={'role': User.RoleChoices.ELEVE}
    )
    
    # Identifiant unique élève (matricule)
    matricule = models.CharField(
        _('matricule'),
        max_length=20,
        unique=True,
        help_text=_("Ex: 2026/001/EL")
    )
    
    # Classe actuelle (relation vers pedagogie.Classe)
    classe_actuelle = models.ForeignKey(
        'pedagogie.Classe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eleves',
        verbose_name=_('classe actuelle')
    )
    
    # Informations médicales (important pour urgences)
    groupe_sanguin = models.CharField(
        _('groupe sanguin'),
        max_length=5,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    allergies = models.TextField(_('allergies'), blank=True)
    notes_medicales = models.TextField(_('notes médicales'), blank=True)
    
    # Personne à contacter en urgence
    contact_urgence_nom = models.CharField(_('contact urgence - nom'), max_length=200)
    contact_urgence_phone = models.CharField(_('contact urgence - téléphone'), max_length=20)
    contact_urgence_relation = models.CharField(
        _('contact urgence - relation'),
        max_length=50,
        help_text=_("Ex: Père, Mère, Tuteur")
    )
    
    # Statut
    is_redoublant = models.BooleanField(_('redoublant'), default=False)
    date_admission = models.DateField(_('date d\'admission'))
    
    class Meta:
        verbose_name = _('profil élève')
        verbose_name_plural = _('profils élèves')
        ordering = ['matricule']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.matricule}"


class EnseignantProfile(TimeStampedModel):
    """
    Profil spécifique aux enseignants.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='enseignant_profile',
        limit_choices_to={'role': User.RoleChoices.ENSEIGNANT}
    )
    
    # Informations professionnelles
    numero_cnss = models.CharField(
        _('numéro CNSS'),
        max_length=50,
        blank=True,
        help_text=_("Numéro de sécurité sociale")
    )
    
    diplomes = models.TextField(_('diplômes'), blank=True)
    specialite = models.CharField(_('spécialité'), max_length=100, blank=True)
    
    # Matières enseignées (ManyToMany vers pedagogie.Matiere)
    matieres = models.ManyToManyField(
        'pedagogie.Matiere',
        related_name='enseignants',
        verbose_name=_('matières enseignées'),
        blank=True
    )
    
    # Statut
    is_professeur_principal = models.BooleanField(
        _('professeur principal'),
        default=False
    )
    classe_principale = models.ForeignKey(
        'pedagogie.Classe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='professeur_principal',
        verbose_name=_('classe principale')
    )
    
    date_embauche = models.DateField(_('date d\'embauche'))
    
    class Meta:
        verbose_name = _('profil enseignant')
        verbose_name_plural = _('profils enseignants')
    
    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"


class ParentProfile(TimeStampedModel):
    """
    Profil parent avec lien vers élève(s).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        limit_choices_to={'role': User.RoleChoices.PARENT}
    )
    
    # Lien avec élève(s)
    eleves = models.ManyToManyField(
        EleveProfile,
        related_name='parents',
        verbose_name=_('enfants')
    )
    
    # Type de relation
    relation = models.CharField(
        _('relation'),
        max_length=50,
        choices=[
            ('PERE', _('Père')),
            ('MERE', _('Mère')),
            ('TUTEUR', _('Tuteur légal')),
            ('AUTRE', _('Autre'))
        ]
    )
    
    profession = models.CharField(_('profession'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('profil parent')
        verbose_name_plural = _('profils parents')
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_relation_display()})"


class ComptableProfile(TimeStampedModel):
    """
    Profil comptable.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='comptable_profile',
        limit_choices_to={'role': User.RoleChoices.COMPTABLE}
    )
    
    numero_cnss = models.CharField(_('numéro CNSS'), max_length=50, blank=True)
    date_embauche = models.DateField(_('date d\'embauche'))
    
    class Meta:
        verbose_name = _('profil comptable')
        verbose_name_plural = _('profils comptables')
```

### 4.2 App `pedagogie` - Gestion Pédagogique

```python
# apps/pedagogie/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models imcport TimeStampedModel

class Matiere(TimeStampedModel):
    """
    Matière enseignée (Mathématiques, Français, etc.)
    """
    code = models.CharField(
        _('code'),
        max_length=10,
        unique=True,
        help_text=_("Ex: MATH, FR, ANG")
    )
    nom = models.CharField(_('nom'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    coefficient = models.DecimalField(
        _('coefficient'),
        max_digits=4,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)]
    )
    
    # Couleur pour affichage emploi du temps (hex)
    couleur = models.CharField(
        _('couleur'),
        max_length=7,
        default='#3B82F6',
        help_text=_("Couleur hex pour l'emploi du temps, ex: #3B82F6")
    )
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('matière')
        verbose_name_plural = _('matières')
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} (Coef: {self.coefficient})"


class Classe(TimeStampedModel):
    """
    Classe scolaire (6ème A, Terminale S1, etc.)
    """
    class NiveauChoices(models.TextChoices):
        SIXIEME = '6EME', _('6ème')
        CINQUIEME = '5EME', _('5ème')
        QUATRIEME = '4EME', _('4ème')
        TROISIEME = '3EME', _('3ème')
        SECONDE = '2NDE', _('Seconde')
        PREMIERE = '1ERE', _('Première')
        TERMINALE = 'TLE', _('Terminale')
    
    niveau = models.CharField(
        _('niveau'),
        max_length=10,
        choices=NiveauChoices.choices
    )
    
    nom = models.CharField(
        _('nom'),
        max_length=50,
        help_text=_("Ex: 6ème A, Terminale S1")
    )
    
    # Filière (pour lycée)
    filiere = models.CharField(
        _('filière'),
        max_length=50,
        blank=True,
        help_text=_("Ex: Sciences, Lettres, TSE")
    )
    
    # Année scolaire
    annee_scolaire = models.ForeignKey(
        'administration.AnneeScolaire',
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name=_('année scolaire')
    )
    
    # Professeur principal
    professeur_principal = models.ForeignKey(
        'users.EnseignantProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_principales',
        verbose_name=_('professeur principal')
    )
    
    # Capacité
    capacite_max = models.PositiveIntegerField(
        _('capacité maximale'),
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    # Salle principale
    salle = models.ForeignKey(
        'administration.Salle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes',
        verbose_name=_('salle')
    )
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('classe')
        verbose_name_plural = _('classes')
        ordering = ['niveau', 'nom']
        unique_together = [['nom', 'annee_scolaire']]
    
    def __str__(self):
        return f"{self.nom} - {self.annee_scolaire}"
    
    @property
    def nombre_eleves(self):
        """Retourne le nombre d'élèves actuels"""
        return self.eleves.count()
    
    @property
    def places_disponibles(self):
        """Retourne le nombre de places disponibles"""
        return self.capacite_max - self.nombre_eleves


class EmploiDuTemps(TimeStampedModel):
    """
    Créneau d'emploi du temps
    """
    class JourChoices(models.TextChoices):
        LUNDI = 'LUN', _('Lundi')
        MARDI = 'MAR', _('Mardi')
        MERCREDI = 'MER', _('Mercredi')
        JEUDI = 'JEU', _('Jeudi')
        VENDREDI = 'VEN', _('Vendredi')
        SAMEDI = 'SAM', _('Samedi')
    
    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name='emploi_du_temps',
        verbose_name=_('classe')
    )
    
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='creneaux',
        verbose_name=_('matière')
    )
    
    enseignant = models.ForeignKey(
        'users.EnseignantProfile',
        on_delete=models.CASCADE,
        related_name='creneaux',
        verbose_name=_('enseignant')
    )
    
    jour = models.CharField(
        _('jour'),
        max_length=3,
        choices=JourChoices.choices
    )
    
    heure_debut = models.TimeField(_('heure de début'))
    heure_fin = models.TimeField(_('heure de fin'))
    
    salle = models.ForeignKey(
        'administration.Salle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='creneaux',
        verbose_name=_('salle')
    )
    
    class Meta:
        verbose_name = _('créneau emploi du temps')
        verbose_name_plural = _('emploi du temps')
        ordering = ['jour', 'heure_debut']
        # Éviter chevauchement pour même classe
        unique_together = [['classe', 'jour', 'heure_debut']]
        indexes = [
            models.Index(fields=['classe', 'jour']),
            models.Index(fields=['enseignant', 'jour']),
        ]
    
    def __str__(self):
        return f"{self.classe} - {self.matiere} ({self.jour} {self.heure_debut}-{self.heure_fin})"
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        if self.heure_debut >= self.heure_fin:
            raise ValidationError(_("L'heure de début doit être avant l'heure de fin"))
        
        # Vérifier que l'enseignant enseigne bien cette matière
        if self.matiere not in self.enseignant.matieres.all():
            raise ValidationError(
                _(f"{self.enseignant.user.get_full_name()} n'enseigne pas {self.matiere}")
            )


class Note(TimeStampedModel):
    """
    Note d'un élève pour une matière
    """
    class TypeNoteChoices(models.TextChoices):
        DEVOIR = 'DEVOIR', _('Devoir')
        COMPOSITION = 'COMPOSITION', _('Composition')
        INTERRO = 'INTERRO', _('Interrogation')
        EXAMEN = 'EXAMEN', _('Examen')
        CONTROLE = 'CONTROLE', _('Contrôle continu')
    
    class PeriodeChoices(models.TextChoices):
        TRIMESTRE_1 = 'T1', _('1er Trimestre')
        TRIMESTRE_2 = 'T2', _('2ème Trimestre')
        TRIMESTRE_3 = 'T3', _('3ème Trimestre')
        SEMESTRE_1 = 'S1', _('1er Semestre')
        SEMESTRE_2 = 'S2', _('2ème Semestre')
    
    eleve = models.ForeignKey(
        'users.EleveProfile',
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('élève')
    )
    
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('matière')
    )
    
    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('classe')
    )
    
    annee_scolaire = models.ForeignKey(
        'administration.AnneeScolaire',
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('année scolaire')
    )
    
    type_note = models.CharField(
        _('type de note'),
        max_length=20,
        choices=TypeNoteChoices.choices
    )
    
    periode = models.CharField(
        _('période'),
        max_length=5,
        choices=PeriodeChoices.choices
    )
    
    valeur = models.DecimalField(
        _('note'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    
    sur = models.DecimalField(
        _('sur'),
        max_digits=5,
        decimal_places=2,
        default=20,
        help_text=_("Note maximale possible")
    )
    
    # Coefficient spécifique à cette note (peut différer du coef matière)
    coefficient = models.DecimalField(
        _('coefficient'),
        max_digits=4,
        decimal_places=2,
        default=1.0
    )
    
    appreciation = models.TextField(_('appréciation'), blank=True)
    
    enseignant = models.ForeignKey(
        'users.EnseignantProfile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='notes_saisies',
        verbose_name=_('enseignant')
    )
    
    date_evaluation = models.DateField(_('date d\'évaluation'))
    
    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        ordering = ['-date_evaluation']
        indexes = [
            models.Index(fields=['eleve', 'periode', 'annee_scolaire']),
            models.Index(fields=['classe', 'matiere', 'periode']),
        ]
    
    def __str__(self):
        return f"{self.eleve.user.get_full_name()} - {self.matiere}: {self.valeur}/{self.sur}"
    
    @property
    def note_sur_20(self):
        """Convertit la note sur 20"""
        if self.sur == 20:
            return self.valeur
        return (self.valeur / self.sur) * 20


class Presence(TimeStampedModel):
    """
    Présence/Absence d'un élève
    """
    class StatutChoices(models.TextChoices):
        PRESENT = 'PRESENT', _('Présent')
        ABSENT = 'ABSENT', _('Absent')
        RETARD = 'RETARD', _('Retard')
        ABSENT_JUSTIFIE = 'ABSENT_J', _('Absent justifié')
    
    eleve = models.ForeignKey(
        'users.EleveProfile',
        on_delete=models.CASCADE,
        related_name='presences',
        verbose_name=_('élève')
    )
    
    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name='presences',
        verbose_name=_('classe')
    )
    
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='presences',
        verbose_name=_('matière'),
        help_text=_("Laissez vide pour présence globale journée")
    )
    
    date = models.DateField(_('date'))
    
    statut = models.CharField(
        _('statut'),
        max_length=10,
        choices=StatutChoices.choices,
        default=StatutChoices.PRESENT
    )
    
    justification = models.TextField(_('justification'), blank=True)
    document_justificatif = models.FileField(
        _('document justificatif'),
        upload_to='presences/justificatifs/%Y/%m/',
        blank=True,
        null=True
    )
    
    enregistre_par = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='presences_enregistrees',
        verbose_name=_('enregistré par')
    )
    
    # Notification envoyée aux parents
    notification_envoyee = models.BooleanField(
        _('notification envoyée'),
        default=False
    )
    
    class Meta:
        verbose_name = _('présence')
        verbose_name_plural = _('présences')
        ordering = ['-date']
        unique_together = [['eleve', 'date', 'matiere']]
        indexes = [
            models.Index(fields=['eleve', 'date']),
            models.Index(fields=['classe', 'date']),
        ]
    
    def __str__(self):
        matiere_str = f" - {self.matiere}" if self.matiere else ""
        return f"{self.eleve.user.get_full_name()} - {self.date}{matiere_str}: {self.get_statut_display()}"


class Bulletin(TimeStampedModel):
    """
    Bulletin scolaire d'un élève pour une période
    """
    eleve = models.ForeignKey(
        'users.EleveProfile',
        on_delete=models.CASCADE,
        related_name='bulletins',
        verbose_name=_('élève')
    )
    
    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name='bulletins',
        verbose_name=_('classe')
    )
    
    annee_scolaire = models.ForeignKey(
        'administration.AnneeScolaire',
        on_delete=models.CASCADE,
        related_name='bulletins',
        verbose_name=_('année scolaire')
    )
    
    periode = models.CharField(
        _('période'),
        max_length=5,
        choices=Note.PeriodeChoices.choices
    )
    
    moyenne_generale = models.DecimalField(
        _('moyenne générale'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    
    rang = models.PositiveIntegerField(
        _('rang'),
        help_text=_("Classement dans la classe")
    )
    
    total_eleves = models.PositiveIntegerField(
        _('total élèves'),
        help_text=_("Nombre total d'élèves dans la classe")
    )
    
    # Appréciations
    appreciation_generale = models.TextField(_('appréciation générale'))
    appreciation_prof_principal = models.TextField(
        _('appréciation professeur principal'),
        blank=True
    )
    appreciation_directeur = models.TextField(
        _('appréciation directeur'),
        blank=True
    )
    
    # Statistiques
    total_absences = models.PositiveIntegerField(_('total absences'), default=0)
    total_retards = models.PositiveIntegerField(_('total retards'), default=0)
    
    # Fichier PDF généré
    fichier_pdf = models.FileField(
        _('fichier PDF'),
        upload_to='bulletins/%Y/%m/',
        blank=True,
        null=True
    )
    
    date_generation = models.DateTimeField(
        _('date de génération'),
        auto_now_add=True
    )
    
    est_valide = models.BooleanField(_('validé'), default=False)
    valide_par = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bulletins_valides',
        verbose_name=_('validé par')
    )
    
    class Meta:
        verbose_name = _('bulletin')
        verbose_name_plural = _('bulletins')
        ordering = ['-annee_scolaire', '-periode', 'classe', 'rang']
        unique_together = [['eleve', 'periode', 'annee_scolaire']]
    
    def __str__(self):
        return f"Bulletin {self.eleve.user.get_full_name()} - {self.get_periode_display()} ({self.moyenne_generale}/20)"
```

*Continuons avec les autres apps dans le prochain message pour ne pas dépasser la limite...*

Voulez-vous que je continue avec :
1. App `administration` (Années scolaires, Inscriptions, Salles)
2. App `finances` (Frais, Paiements, Factures)
3. App `communication` (Messages, Notifications)
4. App `bibliotheque` (Documents, Devoirs, Cahier de texte)
5. Les Serializers, Views et Endpoints API

Ou préférez-vous qu'on compile tout dans un document unique maintenant ?
