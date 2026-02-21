"""
Views pour l'authentification par cookies JWT.

Endpoints :
  POST   /auth/login/           → connexion, pose cookies
  POST   /auth/logout/          → supprime cookies
  POST   /auth/refresh/         → renouvelle access_token via refresh cookie
  GET    /auth/me/              → profil utilisateur connecté
  PATCH  /auth/me/              → mise à jour profil
  POST   /auth/change-password/ → changement mot de passe
  POST   /auth/reset-password/  → demande de réinitialisation
  POST   /auth/reset-password/confirm/ → confirmation réinitialisation
  GET    /auth/users/           → liste utilisateurs (admin)
  POST   /auth/users/           → créer un utilisateur (admin)
  GET    /auth/users/<pk>/      → détail utilisateur (admin)
  PATCH  /auth/users/<pk>/      → modifier utilisateur (admin)
  DELETE /auth/users/<pk>/      → désactiver utilisateur (admin)
"""
import jwt
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from core.pagination import StandardResultsSetPagination
from core.permissions import IsAdmin

from .authentication import CookieJWTAuthentication
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer,
)
from .services import (
    set_auth_cookies,
    delete_auth_cookies,
    decode_refresh_token,
    generate_access_token,
    get_user_data,
    REFRESH_COOKIE,
    ACCESS_LIFE,
)

User = get_user_model()
logger = logging.getLogger('authentication')


# ─── Login / Logout / Refresh ─────────────────────────────────────────────────

class LoginView(APIView):
    """
    POST /auth/login/
    Body: { "username": "...", "password": "..." }
    Réponse: données utilisateur + cookies access_token & refresh_token
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Pas d'auth requise pour se connecter

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        response = Response({
            'message': _('Connexion réussie.'),
            'user': get_user_data(user),
        }, status=status.HTTP_200_OK)

        set_auth_cookies(response, user)
        return response


class LogoutView(APIView):
    """
    POST /auth/logout/
    Supprime les cookies d'authentification.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({'message': _('Déconnexion réussie.')}, status=status.HTTP_200_OK)
        delete_auth_cookies(response)
        return response


class RefreshTokenView(APIView):
    """
    POST /auth/refresh/
    Lit le cookie refresh_token et émet un nouveau access_token.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(REFRESH_COOKIE())
        if not refresh_token:
            return Response(
                {'detail': _('Refresh token manquant.')},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = decode_refresh_token(refresh_token)
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail': _('Session expirée. Veuillez vous reconnecter.')},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return Response(
                {'detail': _('Token invalide.')},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist:
            return Response(
                {'detail': _('Utilisateur introuvable.')},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'detail': _('Compte désactivé.')},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        new_access = generate_access_token(user)

        response = Response({
            'message': _('Token renouvelé.'),
            'user': get_user_data(user),
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            getattr(settings, 'JWT_ACCESS_COOKIE', 'access_token'),
            new_access,
            max_age=int(ACCESS_LIFE().total_seconds()),
            httponly=True,
            secure=getattr(settings, 'JWT_COOKIE_SECURE', not settings.DEBUG),
            samesite=getattr(settings, 'JWT_COOKIE_SAMESITE', 'Lax'),
            path=getattr(settings, 'JWT_COOKIE_PATH', '/'),
        )
        return response


# ─── Profil personnel ─────────────────────────────────────────────────────────

class MeView(APIView):
    """
    GET  /auth/me/ → profil complet de l'utilisateur connecté
    PATCH /auth/me/ → mise à jour du profil (champs autorisés seulement)
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Retourner le profil complet mis à jour
        return Response(
            UserSerializer(request.user, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


# ─── Gestion des mots de passe ────────────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    POST /auth/change-password/
    Body: { "old_password", "new_password", "confirm_password" }
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])

        # Invalider la session en cours (forcer une nouvelle connexion)
        response = Response(
            {'message': _('Mot de passe modifié avec succès. Veuillez vous reconnecter.')},
            status=status.HTTP_200_OK,
        )
        delete_auth_cookies(response)
        return response


class ResetPasswordRequestView(APIView):
    """
    POST /auth/reset-password/
    Body: { "email": "..." }
    Déclenche l'envoi d'un email de réinitialisation (via Celery task).
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Import ici pour éviter les imports circulaires
        try:
            from .tasks import send_password_reset_email
            send_password_reset_email.delay(user.pk)
        except Exception:
            logger.exception('Erreur envoi email reset pour user %s', user.pk)

        # Toujours retourner 200 pour ne pas divulguer les emails existants
        return Response(
            {'message': _('Si ce compte existe, un email de réinitialisation a été envoyé.')},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(APIView):
    """
    POST /auth/reset-password/confirm/
    Body: { "token", "new_password", "confirm_password" }
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[getattr(settings, 'JWT_ALGORITHM', 'HS256')],
            )
            if payload.get('type') != 'password_reset':
                raise jwt.InvalidTokenError()
        except jwt.ExpiredSignatureError:
            return Response(
                {'detail': _('Lien de réinitialisation expiré.')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.InvalidTokenError:
            return Response(
                {'detail': _('Lien de réinitialisation invalide.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist:
            return Response(
                {'detail': _('Utilisateur introuvable.')},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response(
            {'message': _('Mot de passe réinitialisé avec succès.')},
            status=status.HTTP_200_OK,
        )


# ─── Gestion des utilisateurs (Admin) ────────────────────────────────────────

class UserListCreateView(ListCreateAPIView):
    """
    GET  /auth/users/ → liste paginée des utilisateurs (admin)
    POST /auth/users/ → créer un utilisateur (admin)
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def get_queryset(self):
        qs = User.objects.all()
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')
        search = self.request.query_params.get('search')

        if role:
            qs = qs.filter(role=role)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        if search:
            qs = qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                email__icontains=search
            ) | qs.filter(
                username__icontains=search
            )
        return qs.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class UserDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /auth/users/<pk>/ → détail d'un utilisateur
    PATCH  /auth/users/<pk>/ → modifier un utilisateur
    DELETE /auth/users/<pk>/ → désactiver (soft delete) un utilisateur
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            UserSerializer(instance, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete : désactive le compte sans le supprimer."""
        instance = self.get_object()
        if instance == request.user:
            return Response(
                {'detail': _('Vous ne pouvez pas désactiver votre propre compte.')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(
            {'message': _('Utilisateur désactivé avec succès.')},
            status=status.HTTP_200_OK,
        )