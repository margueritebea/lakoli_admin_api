# apps/pedagogie/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimeStampedModel

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
        CP1 = 'CP1', _('CP1') 
        CP2 = 'CP2', _('CP2') 
        CE1 = 'CE1', _('CE1')
        CE2 = 'CE2', _('CE2') 
        CM1 = 'CM1', _('CM1') 
        CM2 = 'CM2', _('CM2') 

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
        'authentication.EnseignantProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_principales',
        verbose_name=_('professeur principal')
    )
    
    # Capacité
    capacite_max = models.PositiveIntegerField(
        _('capacité maximale'),
        default=50,
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
        DIMANCHE = "DIM", _('Dimanche')
    
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
        'authentication.EnseignantProfile',
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
        'authentication.EleveProfile',
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
        'authentication.EnseignantProfile',
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
        'authentication.EleveProfile',
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
        'authentication.User',
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
        'authentication.EleveProfile',
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
        'authentication.User',
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