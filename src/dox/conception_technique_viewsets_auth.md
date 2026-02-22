# Documentation Technique Backend - API ViewSets & Authentification

## 5.3 ViewSets & Routes API

### Structure des ViewSets

```python
# apps/users/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsAdmin, IsEnseignant, IsEleve, IsParent
from .models import User, EleveProfile, EnseignantProfile, ParentProfile
from .serializers import (
    UserSerializer, EleveProfileSerializer,
    EnseignantProfileSerializer, ParentProfileSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_name']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Permissions personnalisées selon l'action"""
        if self.action == 'create':
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        elif self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retourne l'utilisateur connecté avec son profil"""
        serializer = self.get_serializer(request.user)
        data = serializer.data
        
        # Ajouter le profil selon le rôle
        if request.user.is_eleve and hasattr(request.user, 'eleve_profile'):
            data['profile'] = EleveProfileSerializer(request.user.eleve_profile).data
        elif request.user.is_enseignant and hasattr(request.user, 'enseignant_profile'):
            data['profile'] = EnseignantProfileSerializer(request.user.enseignant_profile).data
        elif request.user.is_parent and hasattr(request.user, 'parent_profile'):
            data['profile'] = ParentProfileSerializer(request.user.parent_profile).data
        
        return Response(data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_active(self, request, pk=None):
        """Active/désactive un utilisateur"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({
            'status': 'success',
            'is_active': user.is_active
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """Changement de mot de passe"""
        user = self.get_object()
        
        # Vérifier que c'est son propre compte ou admin
        if user != request.user and not request.user.role == User.RoleChoices.ADMIN:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Ancien mot de passe incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'status': 'Mot de passe modifié avec succès'})


class EleveProfileViewSet(viewsets.ModelViewSet):
    """ViewSet pour les profils élèves"""
    queryset = EleveProfile.objects.select_related('user', 'classe_actuelle').all()
    serializer_class = EleveProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['classe_actuelle', 'is_redoublant']
    search_fields = ['matricule', 'user__first_name', 'user__last_name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_classe(self, request):
        """Liste des élèves par classe"""
        classe_id = request.query_params.get('classe_id')
        if not classe_id:
            return Response(
                {'error': 'classe_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eleves = self.queryset.filter(classe_actuelle_id=classe_id)
        serializer = self.get_serializer(eleves, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def bulletin_history(self, request, pk=None):
        """Historique des bulletins d'un élève"""
        eleve = self.get_object()
        from apps.pedagogie.serializers import BulletinSerializer
        bulletins = eleve.bulletins.all().order_by('-annee_scolaire', '-periode')
        serializer = BulletinSerializer(bulletins, many=True)
        return Response(serializer.data)


# apps/pedagogie/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Classe, Matiere, Note, EmploiDuTemps, Presence, Bulletin
from .serializers import (
    ClasseSerializer, MatiereSerializer, NoteSerializer,
    EmploiDuTempsSerializer, PresenceSerializer, BulletinSerializer
)

class ClasseViewSet(viewsets.ModelViewSet):
    """ViewSet pour les classes"""
    queryset = Classe.objects.select_related('annee_scolaire', 'professeur_principal', 'salle').all()
    serializer_class = ClasseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['niveau', 'annee_scolaire', 'is_active']
    search_fields = ['nom', 'filiere']
    
    @action(detail=True, methods=['get'])
    def emploi_du_temps(self, request, pk=None):
        """Emploi du temps d'une classe"""
        classe = self.get_object()
        emploi = classe.emploi_du_temps.all().order_by('jour', 'heure_debut')
        serializer = EmploiDuTempsSerializer(emploi, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def eleves(self, request, pk=None):
        """Liste des élèves de la classe"""
        classe = self.get_object()
        from apps.authentication.serializers import EleveProfileSerializer
        eleves = classe.eleves.all().order_by('user__last_name')
        serializer = EleveProfileSerializer(eleves, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        """Statistiques de la classe"""
        classe = self.get_object()
        
        return Response({
            'nombre_eleves': classe.nombre_eleves,
            'places_disponibles': classe.places_disponibles,
            'taux_remplissage': (classe.nombre_eleves / classe.capacite_max * 100) if classe.capacite_max > 0 else 0,
            'moyenne_generale': self._calculer_moyenne_classe(classe),
        })
    
    def _calculer_moyenne_classe(self, classe):
        """Calcule la moyenne générale de la classe"""
        from django.db.models import Avg
        from apps.administration.models import AnneeScolaire
        
        annee_active = AnneeScolaire.get_annee_active()
        if not annee_active:
            return None
        
        notes = Note.objects.filter(
            classe=classe,
            annee_scolaire=annee_active
        )
        
        if not notes.exists():
            return None
        
        return notes.aggregate(
            moyenne=Avg('valeur')
        )['moyenne']


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notes"""
    queryset = Note.objects.select_related('eleve__user', 'matiere', 'classe', 'enseignant').all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'matiere', 'classe', 'periode', 'annee_scolaire', 'type_note']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsEnseignant() | IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrer selon le rôle de l'utilisateur"""
        user = self.request.user
        
        if user.role == User.RoleChoices.ADMIN:
            return self.queryset
        elif user.role == User.RoleChoices.ENSEIGNANT:
            # Enseignant voit les notes de ses matières
            return self.queryset.filter(matiere__in=user.enseignant_profile.matieres.all())
        elif user.role == User.RoleChoices.ELEVE:
            # Élève voit uniquement ses notes
            return self.queryset.filter(eleve=user.eleve_profile)
        elif user.role == User.RoleChoices.PARENT:
            # Parent voit les notes de ses enfants
            return self.queryset.filter(eleve__in=user.parent_profile.eleves.all())
        
        return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def by_eleve_periode(self, request):
        """Notes d'un élève pour une période"""
        eleve_id = request.query_params.get('eleve_id')
        periode = request.query_params.get('periode')
        
        if not eleve_id or not periode:
            return Response(
                {'error': 'eleve_id et periode requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(
            eleve_id=eleve_id,
            periode=periode
        ).order_by('matiere__nom')
        
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsEnseignant | IsAdmin])
    def saisie_multiple(self, request):
        """Saisie multiple de notes pour une classe"""
        notes_data = request.data.get('notes', [])
        
        if not notes_data:
            return Response(
                {'error': 'Aucune note fournie'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_notes = []
        errors = []
        
        for note_data in notes_data:
            serializer = self.get_serializer(data=note_data)
            if serializer.is_valid():
                serializer.save(enseignant=request.user.enseignant_profile)
                created_notes.append(serializer.data)
            else:
                errors.append({
                    'data': note_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created_notes,
            'errors': errors,
            'total_created': len(created_notes),
            'total_errors': len(errors)
        })


class PresenceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les présences"""
    queryset = Presence.objects.select_related('eleve__user', 'classe', 'matiere').all()
    serializer_class = PresenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'classe', 'date', 'statut']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsEnseignant() | IsAdmin()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsEnseignant | IsAdmin])
    def saisie_classe(self, request):
        """Saisie des présences pour toute une classe"""
        classe_id = request.data.get('classe_id')
        date = request.data.get('date')
        presences_data = request.data.get('presences', [])
        
        if not all([classe_id, date, presences_data]):
            return Response(
                {'error': 'classe_id, date et presences requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_presences = []
        
        for presence_data in presences_data:
            presence_data.update({
                'classe': classe_id,
                'date': date,
                'enregistre_par': request.user.id
            })
            
            serializer = self.get_serializer(data=presence_data)
            if serializer.is_valid():
                presence = serializer.save()
                created_presences.append(serializer.data)
                
                # Envoyer notification si absence
                if presence.statut == Presence.StatutChoices.ABSENT:
                    from apps.communication.tasks import envoyer_notification_absence
                    envoyer_notification_absence.delay(presence.id)
            
        return Response({
            'created': created_presences,
            'total': len(created_presences)
        })


# apps/finances/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import FraisScolaire, Facture, Paiement
from .serializers import FraisScolaireSerializer, FactureSerializer, PaiementSerializer

class FactureViewSet(viewsets.ModelViewSet):
    """ViewSet pour les factures"""
    queryset = Facture.objects.select_related('eleve__user', 'annee_scolaire').all()
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'annee_scolaire', 'statut']
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        user = self.request.user
        
        if user.role == User.RoleChoices.ADMIN or user.role == User.RoleChoices.COMPTABLE:
            return self.queryset
        elif user.role == User.RoleChoices.ELEVE:
            return self.queryset.filter(eleve=user.eleve_profile)
        elif user.role == User.RoleChoices.PARENT:
            return self.queryset.filter(eleve__in=user.parent_profile.eleves.all())
        
        return self.queryset.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generer_pdf(self, request, pk=None):
        """Génère le PDF de la facture"""
        facture = self.get_object()
        from apps.finances.tasks import generer_facture_pdf
        
        # Lancer la tâche asynchrone
        task = generer_facture_pdf.delay(facture.id)
        
        return Response({
            'status': 'Génération en cours',
            'task_id': task.id
        })


class PaiementViewSet(viewsets.ModelViewSet):
    """ViewSet pour les paiements"""
    queryset = Paiement.objects.select_related('facture', 'eleve__user').all()
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture', 'eleve', 'mode_paiement', 'statut']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdmin() | IsComptable()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdmin | IsComptable])
    def valider(self, request, pk=None):
        """Valide un paiement"""
        paiement = self.get_object()
        
        paiement.statut = Paiement.StatutChoices.VALIDE
        paiement.valide_par = request.user
        from django.utils import timezone
        paiement.date_validation = timezone.now()
        paiement.save()
        
        # Envoyer notification
        from apps.communication.tasks import envoyer_notification_paiement
        envoyer_notification_paiement.delay(paiement.id)
        
        return Response({
            'status': 'Paiement validé',
            'paiement': self.get_serializer(paiement).data
        })
```

### 5.4 Configuration des URLs API

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import des ViewSets
from apps.authentication.views import UserViewSet, EleveProfileViewSet, EnseignantProfileViewSet
from apps.pedagogie.views import ClasseViewSet, MatiereViewSet, NoteViewSet, PresenceViewSet
from apps.administration.views import AnneeScolaireViewSet, InscriptionViewSet
from apps.finances.views import FraisScolaireViewSet, FactureViewSet, PaiementViewSet
from apps.communication.views import MessageViewSet, NotificationViewSet, ActualiteViewSet
from apps.bibliotheque.views import DocumentViewSet, DevoirViewSet

# Router API
router = DefaultRouter()

# Users
router.register(r'users', UserViewSet, basename='user')
router.register(r'eleves', EleveProfileViewSet, basename='eleve')
router.register(r'enseignants', EnseignantProfileViewSet, basename='enseignant')

# Pédagogie
router.register(r'classes', ClasseViewSet, basename='classe')
router.register(r'matieres', MatiereViewSet, basename='matiere')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'presences', PresenceViewSet, basename='presence')

# Administration
router.register(r'annees-scolaires', AnneeScolaireViewSet, basename='annee-scolaire')
router.register(r'inscriptions', InscriptionViewSet, basename='inscription')

# Finances
router.register(r'frais-scolaires', FraisScolaireViewSet, basename='frais-scolaire')
router.register(r'factures', FactureViewSet, basename='facture')
router.register(r'paiements', PaiementViewSet, basename='paiement')

# Communication
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'actualites', ActualiteViewSet, basename='actualite')

# Bibliothèque
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'devoirs', DevoirViewSet, basename='devoir')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Routes
    path('api/v1/', include(router.urls)),
    
    # API Auth (DRF browsable API)
    path('api-auth/', include('rest_framework.urls')),
]

# Media files en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

---

## 6. Authentification & Sécurité

### 6.1 Configuration JWT

```python
# config/settings/base.py
from datetime import timedelta

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# En développement, ajouter BrowsableAPI
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )
```

### 6.2 Permissions Personnalisées

```python
# core/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Permission pour administrateurs uniquement"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsEnseignant(permissions.BasePermission):
    """Permission pour enseignants"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ENSEIGNANT'


class IsEleve(permissions.BasePermission):
    """Permission pour élèves"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ELEVE'


class IsParent(permissions.BasePermission):
    """Permission pour parents"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PARENT'


class IsComptable(permissions.BasePermission):
    """Permission pour comptables"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'COMPTABLE'


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission pour propriétaire de l'objet ou admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        
        # Vérifier selon le type d'objet
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'eleve'):
            if request.user.role == 'ELEVE':
                return obj.eleve.user == request.user
            elif request.user.role == 'PARENT':
                return obj.eleve in request.user.parent_profile.eleves.all()
        
        return False
```

Voulez-vous que je continue avec :
1. Configuration Celery pour tâches asynchrones
2. Tests unitaires et d'intégration
3. Configuration Docker
4. Guide de déploiement
5. Documentation Postman/OpenAPI ?
