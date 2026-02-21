"""
Authentification par cookies HTTP-only pour DRF.
Remplace le TokenAuthentication standard.

Flow:
  POST /auth/login/  → set cookies access_token + refresh_token
  Toutes les requêtes → CookieJWTAuthentication lit le cookie access_token
  POST /auth/refresh/ → lit refresh_token cookie, émet nouveau access_token
  POST /auth/logout/  → supprime les deux cookies
"""
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
import jwt
from datetime import datetime, timezone


class CookieJWTAuthentication(BaseAuthentication):
    """
    Lit le JWT depuis le cookie HTTP-only 'access_token'.
    Compatible DRF : retourne (user, token_payload) ou None.
    """

    ACCESS_COOKIE = getattr(settings, 'JWT_ACCESS_COOKIE', 'access_token')

    def authenticate(self, request):
        token = request.COOKIES.get(self.ACCESS_COOKIE)
        if not token:
            return None  # Pas de cookie → authentification anonyme

        return self._decode_and_get_user(token)

    def _decode_and_get_user(self, token):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        secret = settings.SECRET_KEY
        algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')

        try:
            payload = jwt.decode(token, secret, algorithms=[algorithm])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(_('Token expiré. Veuillez vous reconnecter.'))
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(_('Token invalide.'))

        user_id = payload.get('user_id')
        if user_id is None:
            raise AuthenticationFailed(_('Payload du token invalide.'))

        try:
            user = User.objects.select_related().get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('Utilisateur introuvable.'))

        if not user.is_active:
            raise AuthenticationFailed(_('Compte désactivé.'))

        return (user, payload)

    def authenticate_header(self, request):
        # Indique au client que l'auth se fait par cookie (pas Bearer)
        return 'Cookie realm="api"'