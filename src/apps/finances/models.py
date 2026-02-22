# apps/finances/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import TimeStampedModel

class FraisScolaire(TimeStampedModel):
    """
    Type de frais (scolarité, inscription, activités, etc.)
    """
    class TypeFraisChoices(models.TextChoices):
        SCOLARITE = 'SCOLARITE', _('Frais de scolarité')
        INSCRIPTION = 'INSCRIPTION', _('Frais d\'inscription')
        REINSCRIPTION = 'REINSCRIPTION', _('Frais de réinscription')
        EXAMEN = 'EXAMEN', _('Frais d\'examen')
        TRANSPORT = 'TRANSPORT', _('Transport scolaire')
        CANTINE = 'CANTINE', _('Cantine')
        ACTIVITES = 'ACTIVITES', _('Activités extrascolaires')
        TENUE = 'TENUE', _('Tenue scolaire')
        MATERIEL = 'MATERIEL', _('Matériel pédagogique')
        BIBLIOTHEQUE = 'BIBLIO', _('Bibliothèque')
        AUTRE = 'AUTRE', _('Autre')
    
    nom = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    type_frais = models.CharField(
        _('type'),
        max_length=20,
        choices=TypeFraisChoices.choices
    )
    
    montant = models.DecimalField(
        _('montant'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Optionnel: montants différents par niveau
    montant_par_niveau = models.JSONField(
        _('montant par niveau'),
        blank=True,
        null=True,
        help_text=_('Ex: {"6EME": 500000, "TLE": 750000}')
    )
    
    annee_scolaire = models.ForeignKey(
        'administration.AnneeScolaire',
        on_delete=models.CASCADE,
        related_name='frais_scolaires',
        verbose_name=_('année scolaire')
    )
    
    # Périodicité
    est_payable_en_tranches = models.BooleanField(
        _('payable en tranches'),
        default=True
    )
    nombre_tranches = models.PositiveIntegerField(
        _('nombre de tranches'),
        default=3,
        validators=[MinValueValidator(1)]
    )
    
    # Dates limites de paiement
    date_limite_1ere_tranche = models.DateField(_('date limite 1ère tranche'), null=True, blank=True)
    date_limite_2eme_tranche = models.DateField(_('date limite 2ème tranche'), null=True, blank=True)
    date_limite_3eme_tranche = models.DateField(_('date limite 3ème tranche'), null=True, blank=True)
    
    is_obligatoire = models.BooleanField(_('obligatoire'), default=True)
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('frais scolaire')
        verbose_name_plural = _('frais scolaires')
        ordering = ['type_frais', 'nom']
    
    def __str__(self):
        return f"{self.nom} - {self.montant} GNF ({self.annee_scolaire})"
    
    def get_montant_pour_niveau(self, niveau):
        """Retourne le montant spécifique pour un niveau si défini"""
        if self.montant_par_niveau and niveau in self.montant_par_niveau:
            return Decimal(str(self.montant_par_niveau[niveau]))
        return self.montant
    
    def get_montant_tranche(self):
        """Retourne le montant d'une tranche"""
        if self.est_payable_en_tranches:
            return self.montant / self.nombre_tranches
        return self.montant


class Facture(TimeStampedModel):
    """
    Facture générée pour un élève
    """
    class StatutChoices(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        EMISE = 'EMISE', _('Émise')
        PARTIELLEMENT_PAYEE = 'PARTIELLE', _('Partiellement payée')
        PAYEE = 'PAYEE', _('Payée')
        ANNULEE = 'ANNULEE', _('Annulée')
    
    numero = models.CharField(
        _('numéro de facture'),
        max_length=50,
        unique=True,
        help_text=_("Ex: FACT-2026-001")
    )
    
    eleve = models.ForeignKey(
        'authentication.EleveProfile',
        on_delete=models.CASCADE,
        related_name='factures',
        verbose_name=_('élève')
    )
    
    annee_scolaire = models.ForeignKey(
        'administration.AnneeScolaire',
        on_delete=models.CASCADE,
        related_name='factures',
        verbose_name=_('année scolaire')
    )
    
    # Lignes de facturation (JSON)
    lignes = models.JSONField(
        _('lignes de facture'),
        help_text=_('Liste des frais: [{"frais_id": 1, "designation": "...", "montant": 500000}, ...]')
    )
    
    montant_total = models.DecimalField(
        _('montant total'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    montant_paye = models.DecimalField(
        _('montant payé'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    montant_restant = models.DecimalField(
        _('montant restant'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    statut = models.CharField(
        _('statut'),
        max_length=15,
        choices=StatutChoices.choices,
        default=StatutChoices.BROUILLON
    )
    
    date_emission = models.DateField(_('date d\'émission'))
    date_echeance = models.DateField(_('date d\'échéance'))
    
    # Remises/Bourses
    remise_pourcentage = models.DecimalField(
        _('remise (%)'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    remise_montant = models.DecimalField(
        _('remise (montant)'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    motif_remise = models.CharField(_('motif remise'), max_length=200, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    # Fichier PDF
    fichier_pdf = models.FileField(
        _('facture PDF'),
        upload_to='factures/%Y/%m/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('facture')
        verbose_name_plural = _('factures')
        ordering = ['-date_emission']
        indexes = [
            models.Index(fields=['eleve', 'annee_scolaire']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.numero} - {self.eleve.user.get_full_name()} ({self.montant_total} GNF)"
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant restant"""
        self.montant_restant = self.montant_total - self.montant_paye
        
        # Mise à jour du statut
        if self.montant_restant <= 0:
            self.statut = self.StatutChoices.PAYEE
        elif self.montant_paye > 0:
            self.statut = self.StatutChoices.PARTIELLEMENT_PAYEE
        elif self.statut == self.StatutChoices.BROUILLON:
            self.statut = self.StatutChoices.EMISE
        
        super().save(*args, **kwargs)


class Paiement(TimeStampedModel):
    """
    Paiement effectué par un élève/parent
    """
    class ModePaiementChoices(models.TextChoices):
        ESPECES = 'ESPECES', _('Espèces')
        CHEQUE = 'CHEQUE', _('Chèque')
        VIREMENT = 'VIREMENT', _('Virement bancaire')
        MOBILE_MONEY = 'MOBILE', _('Mobile Money')
        ORANGE_MONEY = 'ORANGE', _('Orange Money')
        MTN_MOMO = 'MTN', _('MTN Mobile Money')
        CARTE_BANCAIRE = 'CARTE', _('Carte bancaire')
    
    class StatutChoices(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        VALIDE = 'VALIDE', _('Validé')
        ECHOUE = 'ECHOUE', _('Échoué')
        ANNULE = 'ANNULE', _('Annulé')
        REMBOURSE = 'REMBOURSE', _('Remboursé')
    
    numero_recu = models.CharField(
        _('numéro de reçu'),
        max_length=50,
        unique=True,
        help_text=_("Ex: RECU-2026-001")
    )
    
    facture = models.ForeignKey(
        Facture,
        on_delete=models.CASCADE,
        related_name='paiements',
        verbose_name=_('facture')
    )
    
    eleve = models.ForeignKey(
        'authentication.EleveProfile',
        on_delete=models.CASCADE,
        related_name='paiements',
        verbose_name=_('élève')
    )
    
    montant = models.DecimalField(
        _('montant payé'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    mode_paiement = models.CharField(
        _('mode de paiement'),
        max_length=15,
        choices=ModePaiementChoices.choices
    )
    
    # Détails selon mode de paiement
    reference_transaction = models.CharField(
        _('référence transaction'),
        max_length=200,
        blank=True,
        help_text=_("Numéro de chèque, ID transaction mobile money, etc.")
    )
    
    numero_telephone = models.CharField(
        _('numéro de téléphone'),
        max_length=20,
        blank=True,
        help_text=_("Pour Mobile Money")
    )
    
    date_paiement = models.DateTimeField(_('date de paiement'), auto_now_add=True)
    
    statut = models.CharField(
        _('statut'),
        max_length=15,
        choices=StatutChoices.choices,
        default=StatutChoices.EN_ATTENTE
    )
    
    # Validation
    recu_par = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='paiements_recus',
        verbose_name=_('reçu par')
    )
    
    valide_par = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paiements_valides',
        verbose_name=_('validé par')
    )
    date_validation = models.DateTimeField(_('date de validation'), null=True, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    # Reçu PDF
    fichier_recu_pdf = models.FileField(
        _('reçu PDF'),
        upload_to='recus/%Y/%m/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('paiement')
        verbose_name_plural = _('paiements')
        ordering = ['-date_paiement']
        indexes = [
            models.Index(fields=['facture']),
            models.Index(fields=['eleve', 'date_paiement']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.numero_recu} - {self.montant} GNF ({self.get_mode_paiement_display()})"
    
    def save(self, *args, **kwargs):
        """Mise à jour du montant payé de la facture"""
        super().save(*args, **kwargs)
        
        if self.statut == self.StatutChoices.VALIDE:
            # Recalculer le montant payé de la facture
            total_paye = self.facture.paiements.filter(
                statut=self.StatutChoices.VALIDE
            ).aggregate(models.Sum('montant'))['montant__sum'] or Decimal('0.00')
            
            self.facture.montant_paye = total_paye
            self.facture.save()


class RapportFinancier(TimeStampedModel):
    """
    Rapport financier périodique
    """
    class TypeRapportChoices(models.TextChoices):
        JOURNALIER = 'JOUR', _('Journalier')
        HEBDOMADAIRE = 'SEMAINE', _('Hebdomadaire')
        MENSUEL = 'MOIS', _('Mensuel')
        TRIMESTRIEL = 'TRIMESTRE', _('Trimestriel')
        ANNUEL = 'ANNEE', _('Annuel')
    
    titre = models.CharField(_('titre'), max_length=200)
    type_rapport = models.CharField(
        _('type de rapport'),
        max_length=15,
        choices=TypeRapportChoices.choices
    )
    
    date_debut = models.DateField(_('date de début'))
    date_fin = models.DateField(_('date de fin'))
    
    annee_scolaire = models.ForeignKey(
        'administration.AnneeScolaire',
        on_delete=models.CASCADE,
        related_name='rapports_financiers',
        verbose_name=_('année scolaire')
    )
    
    # Statistiques (calculées automatiquement)
    total_factures_emises = models.DecimalField(
        _('total factures émises'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    total_paiements_recus = models.DecimalField(
        _('total paiements reçus'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    total_impayés = models.DecimalField(
        _('total impayés'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    nombre_factures = models.PositiveIntegerField(_('nombre de factures'), default=0)
    nombre_paiements = models.PositiveIntegerField(_('nombre de paiements'), default=0)
    
    # Détails par mode de paiement (JSON)
    details_par_mode = models.JSONField(
        _('détails par mode de paiement'),
        blank=True,
        null=True,
        help_text=_('Ex: {"ESPECES": 5000000, "MOBILE": 3000000}')
    )
    
    # Fichiers
    fichier_excel = models.FileField(
        _('rapport Excel'),
        upload_to='rapports/financiers/%Y/%m/',
        blank=True,
        null=True
    )
    
    fichier_pdf = models.FileField(
        _('rapport PDF'),
        upload_to='rapports/financiers/%Y/%m/',
        blank=True,
        null=True
    )
    
    genere_par = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='rapports_generes',
        verbose_name=_('généré par')
    )
    
    date_generation = models.DateTimeField(_('date de génération'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('rapport financier')
        verbose_name_plural = _('rapports financiers')
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"{self.titre} ({self.date_debut} - {self.date_fin})"