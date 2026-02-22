# Documentation Technique Backend - Suite
## Apps Complémentaires

### 4.3 App `administration` - Gestion Administrative

```python
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
```

### 4.4 App `finances` - Gestion Financière

```python
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
```

Voulez-vous que je continue avec :
1. Apps `communication` et `bibliotheque` 
2. Les Serializers DRF
3. Les Views et Endpoints API
4. Système d'authentification détaillé
5. Configuration Celery pour tâches asynchrones ?
