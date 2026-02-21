# apps/administration/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel

class AnneeScolaire(TimeStampedModel):
    """
    Année scolaire (ex: 2025-2026)
    """
    nom = models.CharField(
        _('nom'),
        max_length=50,
        unique=True,
        help_text=_("Ex: 2025-2026")
    )
    
    date_debut = models.DateField(_('date de début'))
    date_fin = models.DateField(_('date de fin'))
    
    # Périodes (trimestres ou semestres)
    systeme_evaluation = models.CharField(
        _('système d\'évaluation'),
        max_length=20,
        choices=[
            ('TRIMESTRE', _('Trimestres')),
            ('SEMESTRE', _('Semestres'))
        ],
        default='TRIMESTRE'
    )
    
    # Dates des trimestres/semestres
    trimestre1_debut = models.DateField(_('trimestre 1 - début'), null=True, blank=True)
    trimestre1_fin = models.DateField(_('trimestre 1 - fin'), null=True, blank=True)
    trimestre2_debut = models.DateField(_('trimestre 2 - début'), null=True, blank=True)
    trimestre2_fin = models.DateField(_('trimestre 2 - fin'), null=True, blank=True)
    trimestre3_debut = models.DateField(_('trimestre 3 - début'), null=True, blank=True)
    trimestre3_fin = models.DateField(_('trimestre 3 - fin'), null=True, blank=True)
    
    semestre1_debut = models.DateField(_('semestre 1 - début'), null=True, blank=True)
    semestre1_fin = models.DateField(_('semestre 1 - fin'), null=True, blank=True)
    semestre2_debut = models.DateField(_('semestre 2 - début'), null=True, blank=True)
    semestre2_fin = models.DateField(_('semestre 2 - fin'), null=True, blank=True)
    
    est_active = models.BooleanField(
        _('année active'),
        default=False,
        help_text=_("Une seule année peut être active à la fois")
    )
    
    class Meta:
        verbose_name = _('année scolaire')
        verbose_name_plural = _('années scolaires')
        ordering = ['-date_debut']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        """Assurer qu'une seule année est active"""
        if self.est_active:
            # Désactiver toutes les autres années
            AnneeScolaire.objects.filter(est_active=True).exclude(pk=self.pk).update(est_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_annee_active(cls):
        """Retourne l'année scolaire active"""
        return cls.objects.filter(est_active=True).first()


class Inscription(TimeStampedModel):
    """
    Inscription d'un élève pour une année scolaire
    """
    class StatutChoices(models.TextChoices):
        EN_COURS = 'EN_COURS', _('En cours')
        VALIDEE = 'VALIDEE', _('Validée')
        REJETEE = 'REJETEE', _('Rejetée')
        ANNULEE = 'ANNULEE', _('Annulée')
    
    eleve = models.ForeignKey(
        'authentication.EleveProfile',
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name=_('élève')
    )
    
    classe = models.ForeignKey(
        'pedagogie.Classe',
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name=_('classe')
    )
    
    annee_scolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name=_('année scolaire')
    )
    
    date_inscription = models.DateField(_('date d\'inscription'), auto_now_add=True)
    
    statut = models.CharField(
        _('statut'),
        max_length=15,
        choices=StatutChoices.choices,
        default=StatutChoices.EN_COURS
    )
    
    # Documents fournis
    acte_naissance = models.FileField(
        _('acte de naissance'),
        upload_to='inscriptions/actes/%Y/',
        blank=True,
        null=True
    )
    certificat_scolarite_precedent = models.FileField(
        _('certificat scolarité précédent'),
        upload_to='inscriptions/certificats/%Y/',
        blank=True,
        null=True
    )
    photo_identite = models.ImageField(
        _('photo d\'identité'),
        upload_to='inscriptions/photos/%Y/',
        blank=True,
        null=True
    )
    
    # Validation
    validee_par = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscriptions_validees',
        verbose_name=_('validée par')
    )
    date_validation = models.DateTimeField(_('date de validation'), null=True, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('inscription')
        verbose_name_plural = _('inscriptions')
        ordering = ['-date_inscription']
        unique_together = [['eleve', 'annee_scolaire']]
    
    def __str__(self):
        return f"{self.eleve.user.get_full_name()} - {self.classe} ({self.annee_scolaire})"


class Salle(TimeStampedModel):
    """
    Salle de classe
    """
    class TypeSalleChoices(models.TextChoices):
        CLASSE = 'CLASSE', _('Salle de classe')
        LABORATOIRE = 'LABO', _('Laboratoire')
        INFORMATIQUE = 'INFO', _('Salle informatique')
        BIBLIOTHEQUE = 'BIBLIO', _('Bibliothèque')
        CONFERENCE = 'CONF', _('Salle de conférence')
        SPORT = 'SPORT', _('Salle de sport')
    
    numero = models.CharField(
        _('numéro'),
        max_length=20,
        unique=True,
        help_text=_("Ex: A101, LAB-01")
    )
    
    nom = models.CharField(_('nom'), max_length=100, blank=True)
    
    type_salle = models.CharField(
        _('type'),
        max_length=10,
        choices=TypeSalleChoices.choices,
        default=TypeSalleChoices.CLASSE
    )
    
    capacite = models.PositiveIntegerField(
        _('capacité'),
        default=40,
        validators=[MinValueValidator(1)]
    )
    
    batiment = models.CharField(_('bâtiment'), max_length=50, blank=True)
    etage = models.CharField(_('étage'), max_length=20, blank=True)
    
    # Équipements
    a_projecteur = models.BooleanField(_('projecteur'), default=False)
    a_climatisation = models.BooleanField(_('climatisation'), default=False)
    a_tableau_numerique = models.BooleanField(_('tableau numérique'), default=False)
    nombre_ordinateurs = models.PositiveIntegerField(_('nombre d\'ordinateurs'), default=0)
    
    notes = models.TextField(_('notes'), blank=True)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('salle')
        verbose_name_plural = _('salles')
        ordering = ['numero']
    
    def __str__(self):
        return f"{self.numero} ({self.get_type_salle_display()})"


class PersonnelNonEnseignant(TimeStampedModel):
    """
    Personnel administratif et de soutien
    """
    class FonctionChoices(models.TextChoices):
        DIRECTEUR = 'DIRECTEUR', _('Directeur/Directrice')
        SECRETAIRE = 'SECRETAIRE', _('Secrétaire')
        BIBLIOTHECAIRE = 'BIBLIO', _('Bibliothécaire')
        SURVEILLANT = 'SURVEILLANT', _('Surveillant')
        INTENDANT = 'INTENDANT', _('Intendant')
        GARDIEN = 'GARDIEN', _('Gardien')
        AGENT_ENTRETIEN = 'ENTRETIEN', _('Agent d\'entretien')
        TECHNICIEN_INFO = 'TECH_INFO', _('Technicien informatique')
    
    user = models.OneToOneField(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='personnel_profile',
        verbose_name=_('utilisateur')
    )
    
    fonction = models.CharField(
        _('fonction'),
        max_length=20,
        choices=FonctionChoices.choices
    )
    
    numero_cnss = models.CharField(_('numéro CNSS'), max_length=50, blank=True)
    date_embauche = models.DateField(_('date d\'embauche'))
    date_depart = models.DateField(_('date de départ'), null=True, blank=True)
    
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('personnel non enseignant')
        verbose_name_plural = _('personnel non enseignant')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_fonction_display()}"