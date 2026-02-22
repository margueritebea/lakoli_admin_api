# Documentation Technique Backend - API & Communication

### 4.5 App `communication` - Messagerie & Notifications

```python
# apps/communication/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class Message(TimeStampedModel):
    """
    Message interne entre utilisateurs
    """
    expediteur = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='messages_envoyes',
        verbose_name=_('expéditeur')
    )
    
    destinataire = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='messages_recus',
        verbose_name=_('destinataire')
    )
    
    sujet = models.CharField(_('sujet'), max_length=200)
    contenu = models.TextField(_('contenu'))
    
    # Pièces jointes
    fichiers_joints = models.JSONField(
        _('fichiers joints'),
        blank=True,
        null=True,
        help_text=_('Liste des URLs de fichiers joints')
    )
    
    date_envoi = models.DateTimeField(_('date d\'envoi'), auto_now_add=True)
    
    lu = models.BooleanField(_('lu'), default=False)
    date_lecture = models.DateTimeField(_('date de lecture'), null=True, blank=True)
    
    # Message parent (pour réponses/threads)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reponses',
        verbose_name=_('message parent')
    )
    
    # Archivage/Suppression
    archive_par_expediteur = models.BooleanField(_('archivé par expéditeur'), default=False)
    archive_par_destinataire = models.BooleanField(_('archivé par destinataire'), default=False)
    supprime_par_expediteur = models.BooleanField(_('supprimé par expéditeur'), default=False)
    supprime_par_destinataire = models.BooleanField(_('supprimé par destinataire'), default=False)
    
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['-date_envoi']
        indexes = [
            models.Index(fields=['destinataire', 'lu']),
            models.Index(fields=['expediteur', 'date_envoi']),
        ]
    
    def __str__(self):
        return f"{self.expediteur.get_full_name()} → {self.destinataire.get_full_name()}: {self.sujet}"
    
    def marquer_comme_lu(self):
        """Marque le message comme lu"""
        if not self.lu:
            from django.utils import timezone
            self.lu = True
            self.date_lecture = timezone.now()
            self.save()


class Notification(TimeStampedModel):
    """
    Notification système pour l'utilisateur
    """
    class TypeNotificationChoices(models.TextChoices):
        NOUVELLE_NOTE = 'NOTE', _('Nouvelle note')
        ABSENCE = 'ABSENCE', _('Absence signalée')
        RETARD = 'RETARD', _('Retard signalé')
        PAIEMENT = 'PAIEMENT', _('Paiement reçu')
        FACTURE = 'FACTURE', _('Nouvelle facture')
        RAPPEL_PAIEMENT = 'RAPPEL_PAIEMENT', _('Rappel de paiement')
        BULLETIN = 'BULLETIN', _('Bulletin disponible')
        MESSAGE = 'MESSAGE', _('Nouveau message')
        ACTUALITE = 'ACTUALITE', _('Nouvelle actualité')
        EMPLOI_DU_TEMPS = 'EDT', _('Modification emploi du temps')
        DEVOIR = 'DEVOIR', _('Nouveau devoir')
        CONSEIL_CLASSE = 'CONSEIL', _('Conseil de classe')
        AUTRE = 'AUTRE', _('Autre')
    
    utilisateur = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('utilisateur')
    )
    
    type_notification = models.CharField(
        _('type'),
        max_length=20,
        choices=TypeNotificationChoices.choices
    )
    
    titre = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))
    
    # Lien vers l'objet concerné (optionnel)
    lien_url = models.CharField(_('lien URL'), max_length=500, blank=True)
    
    # Métadonnées (JSON) pour informations supplémentaires
    metadata = models.JSONField(
        _('métadonnées'),
        blank=True,
        null=True,
        help_text=_('Données additionnelles en JSON')
    )
    
    date = models.DateTimeField(_('date'), auto_now_add=True)
    lu = models.BooleanField(_('lu'), default=False)
    date_lecture = models.DateTimeField(_('date de lecture'), null=True, blank=True)
    
    # Envoi par email/SMS
    envoyer_par_email = models.BooleanField(_('envoyer par email'), default=False)
    email_envoye = models.BooleanField(_('email envoyé'), default=False)
    
    envoyer_par_sms = models.BooleanField(_('envoyer par SMS'), default=False)
    sms_envoye = models.BooleanField(_('SMS envoyé'), default=False)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['utilisateur', 'lu']),
            models.Index(fields=['type_notification', 'date']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.get_full_name()} - {self.titre}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.lu:
            from django.utils import timezone
            self.lu = True
            self.date_lecture = timezone.now()
            self.save()


class Actualite(TimeStampedModel):
    """
    Actualités et annonces de l'école
    """
    class CategorieChoices(models.TextChoices):
        GENERALE = 'GENERALE', _('Actualité générale')
        EVENEMENT = 'EVENEMENT', _('Événement')
        VACANCES = 'VACANCES', _('Vacances')
        EXAMEN = 'EXAMEN', _('Examen')
        SORTIE = 'SORTIE', _('Sortie éducative')
        REUNION = 'REUNION', _('Réunion')
        COMPETITION = 'COMPETITION', _('Compétition')
        AUTRE = 'AUTRE', _('Autre')
    
    titre = models.CharField(_('titre'), max_length=200)
    contenu = models.TextField(_('contenu'))
    
    categorie = models.CharField(
        _('catégorie'),
        max_length=20,
        choices=CategorieChoices.choices,
        default=CategorieChoices.GENERALE
    )
    
    # Image mise en avant
    image = models.ImageField(
        _('image'),
        upload_to='actualites/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Fichiers joints (PDF, documents)
    fichiers_joints = models.JSONField(
        _('fichiers joints'),
        blank=True,
        null=True
    )
    
    # Ciblage
    destinataires_roles = models.JSONField(
        _('rôles destinataires'),
        default=list,
        help_text=_('Liste des rôles concernés: ["ELEVE", "PARENT", "ENSEIGNANT"]')
    )
    
    classes_ciblees = models.ManyToManyField(
        'pedagogie.Classe',
        related_name='actualites',
        blank=True,
        verbose_name=_('classes ciblées'),
        help_text=_('Laisser vide pour toutes les classes')
    )
    
    # Publication
    date_publication = models.DateTimeField(_('date de publication'))
    date_expiration = models.DateTimeField(
        _('date d\'expiration'),
        null=True,
        blank=True,
        help_text=_('Laisser vide pour pas d\'expiration')
    )
    
    est_epinglee = models.BooleanField(_('épinglée'), default=False)
    est_publiee = models.BooleanField(_('publiée'), default=False)
    
    auteur = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='actualites_creees',
        verbose_name=_('auteur')
    )
    
    nombre_vues = models.PositiveIntegerField(_('nombre de vues'), default=0)
    
    class Meta:
        verbose_name = _('actualité')
        verbose_name_plural = _('actualités')
        ordering = ['-est_epinglee', '-date_publication']
        indexes = [
            models.Index(fields=['est_publiee', 'date_publication']),
            models.Index(fields=['categorie']),
        ]
    
    def __str__(self):
        return self.titre
```

### 4.6 App `bibliotheque` - Ressources Pédagogiques

```python
# apps/bibliotheque/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class CategorieDocument(TimeStampedModel):
    """
    Catégorie de documents
    """
    nom = models.CharField(_('nom'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icone = models.CharField(_('icône'), max_length=50, blank=True, help_text=_("Classe CSS icône"))
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sous_categories',
        verbose_name=_('catégorie parente')
    )
    
    ordre = models.PositiveIntegerField(_('ordre'), default=0)
    
    class Meta:
        verbose_name = _('catégorie de document')
        verbose_name_plural = _('catégories de documents')
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.nom} > {self.nom}"
        return self.nom


class Document(TimeStampedModel):
    """
    Document pédagogique (cours, exercices, etc.)
    """
    class TypeDocumentChoices(models.TextChoices):
        COURS = 'COURS', _('Cours')
        EXERCICE = 'EXERCICE', _('Exercice')
        CORRIGE = 'CORRIGE', _('Corrigé')
        FICHE = 'FICHE', _('Fiche')
        EVALUATION = 'EVALUATION', _('Évaluation')
        SUJET_EXAMEN = 'SUJET', _('Sujet d\'examen')
        MANUEL = 'MANUEL', _('Manuel')
        VIDEO = 'VIDEO', _('Vidéo')
        AUDIO = 'AUDIO', _('Audio')
        AUTRE = 'AUTRE', _('Autre')
    
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    type_document = models.CharField(
        _('type'),
        max_length=20,
        choices=TypeDocumentChoices.choices
    )
    
    categorie = models.ForeignKey(
        CategorieDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('catégorie')
    )
    
    # Fichier
    fichier = models.FileField(
        _('fichier'),
        upload_to='bibliotheque/%Y/%m/'
    )
    
    taille_fichier = models.BigIntegerField(
        _('taille (bytes)'),
        default=0
    )
    
    type_mime = models.CharField(_('type MIME'), max_length=100, blank=True)
    
    # Métadonnées pédagogiques
    matiere = models.ForeignKey(
        'pedagogie.Matiere',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('matière')
    )
    
    classes_ciblees = models.ManyToManyField(
        'pedagogie.Classe',
        related_name='documents',
        blank=True,
        verbose_name=_('classes ciblées')
    )
    
    niveaux_cibles = models.JSONField(
        _('niveaux ciblés'),
        blank=True,
        null=True,
        help_text=_('Liste des niveaux: ["6EME", "5EME"]')
    )
    
    # Versioning
    version = models.CharField(_('version'), max_length=20, default='1.0')
    document_precedent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions_suivantes',
        verbose_name=_('version précédente')
    )
    
    # Accès
    est_public = models.BooleanField(
        _('public'),
        default=False,
        help_text=_("Accessible à tous ou seulement enseignants")
    )
    
    est_telechargeable = models.BooleanField(_('téléchargeable'), default=True)
    
    # Upload
    uploade_par = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='documents_uploades',
        verbose_name=_('uploadé par')
    )
    
    # Statistiques
    nombre_telechargements = models.PositiveIntegerField(_('nombre de téléchargements'), default=0)
    nombre_vues = models.PositiveIntegerField(_('nombre de vues'), default=0)
    
    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['matiere', 'type_document']),
            models.Index(fields=['est_public']),
        ]
    
    def __str__(self):
        return self.titre


class CahierDeTexte(TimeStampedModel):
    """
    Entrée du cahier de texte (contenu du cours)
    """
    classe = models.ForeignKey(
        'pedagogie.Classe',
        on_delete=models.CASCADE,
        related_name='cahier_de_texte',
        verbose_name=_('classe')
    )
    
    matiere = models.ForeignKey(
        'pedagogie.Matiere',
        on_delete=models.CASCADE,
        related_name='cahier_de_texte',
        verbose_name=_('matière')
    )
    
    enseignant = models.ForeignKey(
        'users.EnseignantProfile',
        on_delete=models.CASCADE,
        related_name='cahier_de_texte',
        verbose_name=_('enseignant')
    )
    
    date = models.DateField(_('date du cours'))
    heure_debut = models.TimeField(_('heure de début'))
    heure_fin = models.TimeField(_('heure de fin'))
    
    # Contenu
    titre = models.CharField(_('titre'), max_length=200)
    contenu = models.TextField(_('contenu du cours'))
    
    # Travail à faire
    devoirs_a_faire = models.TextField(_('devoirs à faire'), blank=True)
    
    # Documents liés
    documents = models.ManyToManyField(
        Document,
        related_name='seances',
        blank=True,
        verbose_name=_('documents')
    )
    
    # Validation
    est_valide = models.BooleanField(_('validé'), default=False)
    
    class Meta:
        verbose_name = _('entrée cahier de texte')
        verbose_name_plural = _('cahier de texte')
        ordering = ['-date', 'heure_debut']
        unique_together = [['classe', 'matiere', 'date', 'heure_debut']]
    
    def __str__(self):
        return f"{self.classe} - {self.matiere} ({self.date}): {self.titre}"


class Devoir(TimeStampedModel):
    """
    Devoir à rendre
    """
    class StatutChoices(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        PUBLIE = 'PUBLIE', _('Publié')
        TERMINE = 'TERMINE', _('Terminé')
        ANNULE = 'ANNULE', _('Annulé')
    
    classe = models.ForeignKey(
        'pedagogie.Classe',
        on_delete=models.CASCADE,
        related_name='devoirs',
        verbose_name=_('classe')
    )
    
    matiere = models.ForeignKey(
        'pedagogie.Matiere',
        on_delete=models.CASCADE,
        related_name='devoirs',
        verbose_name=_('matière')
    )
    
    enseignant = models.ForeignKey(
        'users.EnseignantProfile',
        on_delete=models.CASCADE,
        related_name='devoirs_donnes',
        verbose_name=_('enseignant')
    )
    
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    
    # Dates
    date_distribution = models.DateTimeField(_('date de distribution'))
    date_rendu = models.DateTimeField(_('date limite de rendu'))
    
    # Fichier du devoir (sujet)
    fichier = models.FileField(
        _('fichier'),
        upload_to='devoirs/sujets/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Documents de référence
    documents_reference = models.ManyToManyField(
        Document,
        related_name='devoirs',
        blank=True,
        verbose_name=_('documents de référence')
    )
    
    statut = models.CharField(
        _('statut'),
        max_length=15,
        choices=StatutChoices.choices,
        default=StatutChoices.BROUILLON
    )
    
    # Coefficient/Note
    est_note = models.BooleanField(_('noté'), default=True)
    coefficient = models.DecimalField(
        _('coefficient'),
        max_digits=4,
        decimal_places=2,
        default=1.0,
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('devoir')
        verbose_name_plural = _('devoirs')
        ordering = ['-date_distribution']
    
    def __str__(self):
        return f"{self.classe} - {self.matiere}: {self.titre}"


class RenduDevoir(TimeStampedModel):
    """
    Rendu de devoir par un élève
    """
    class StatutChoices(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        RENDU = 'RENDU', _('Rendu')
        EN_RETARD = 'RETARD', _('Rendu en retard')
        NOTE = 'NOTE', _('Noté')
        NON_RENDU = 'NON_RENDU', _('Non rendu')
    
    devoir = models.ForeignKey(
        Devoir,
        on_delete=models.CASCADE,
        related_name='rendus',
        verbose_name=_('devoir')
    )
    
    eleve = models.ForeignKey(
        'users.EleveProfile',
        on_delete=models.CASCADE,
        related_name='devoirs_rendus',
        verbose_name=_('élève')
    )
    
    # Fichier rendu
    fichier = models.FileField(
        _('fichier rendu'),
        upload_to='devoirs/rendus/%Y/%m/',
        blank=True,
        null=True
    )
    
    commentaire_eleve = models.TextField(_('commentaire élève'), blank=True)
    
    date_rendu = models.DateTimeField(_('date de rendu'), null=True, blank=True)
    
    statut = models.CharField(
        _('statut'),
        max_length=15,
        choices=StatutChoices.choices,
        default=StatutChoices.EN_ATTENTE
    )
    
    # Notation
    note_obtenue = models.DecimalField(
        _('note obtenue'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    commentaire_enseignant = models.TextField(_('commentaire enseignant'), blank=True)
    
    date_notation = models.DateTimeField(_('date de notation'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('rendu de devoir')
        verbose_name_plural = _('rendus de devoirs')
        ordering = ['-date_rendu']
        unique_together = [['devoir', 'eleve']]
    
    def __str__(self):
        return f"{self.eleve.user.get_full_name()} - {self.devoir.titre}"
```

---

## 5. API REST - Serializers & Endpoints

### 5.1 Structure Générale des Serializers

```python
# core/serializers.py - Base classes
from rest_framework import serializers

class TimeStampedSerializer(serializers.ModelSerializer):
    """Serializer de base avec timestamps"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer minimal pour User (pour relations)"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        from apps.users.models import User
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'photo']
        read_only_fields = fields
```

### 5.2 Serializers Users

```python
# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EleveProfile, EnseignantProfile, ParentProfile
from core.serializers import TimeStampedSerializer, UserBasicSerializer

User = get_user_model()

class UserSerializer(TimeStampedSerializer):
    """Serializer complet User"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'address', 'photo', 'date_of_birth',
            'preferred_language', 'is_verified', 'is_active',
            'created_at', 'updated_at', 'password'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def create(self, validated_data):
        """Création avec hachage du mot de passe"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Mise à jour avec hachage du mot de passe"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EleveProfileSerializer(TimeStampedSerializer):
    """Serializer profil élève"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    classe_actuelle_nom = serializers.CharField(source='classe_actuelle.nom', read_only=True)
    
    class Meta:
        model = EleveProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnseignantProfileSerializer(TimeStampedSerializer):
    """Serializer profil enseignant"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    matieres_details = serializers.SerializerMethodField()
    
    class Meta:
        model = EnseignantProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_matieres_details(self, obj):
        """Retourne les détails des matières"""
        from apps.pedagogie.serializers import MatiereSerializer
        return MatiereSerializer(obj.matieres.all(), many=True).data


class ParentProfileSerializer(TimeStampedSerializer):
    """Serializer profil parent"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    eleves_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ParentProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_eleves_details(self, obj):
        """Retourne les détails des élèves"""
        return EleveProfileSerializer(obj.eleves.all(), many=True).data
```

Voulez-vous que je continue avec :
1. Les Serializers des autres apps (pedagogie, finances, etc.)
2. Les ViewSets et endpoints API complets
3. Le système d'authentification (JWT, permissions)
4. Configuration Celery pour tâches asynchrones
5. Les tests unitaires et d'intégration ?
