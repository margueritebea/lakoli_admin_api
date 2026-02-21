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
        verbose_name = _('User')
        verbose_name_plural = _('Users')
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
        related_name='enseignant_principal',
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