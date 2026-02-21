"""
Service layer pour l'authentification.
Gère la génération de JWT et la pose/suppression des cookies.
"""
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import HttpResponse

def _cfg(key, default):
    return getattr(settings, key, default)


SECRET       = lambda: _cfg('JWT_SECRET', settings.SECRET_KEY)
ALGORITHM    = lambda: _cfg('JWT_ALGORITHM', 'HS256')
ACCESS_LIFE  = lambda: _cfg('JWT_ACCESS_LIFETIME', timedelta(minutes=30))
REFRESH_LIFE = lambda: _cfg('JWT_REFRESH_LIFETIME', timedelta(days=7))
ACCESS_COOKIE  = lambda: _cfg('JWT_ACCESS_COOKIE', 'access_token')
REFRESH_COOKIE = lambda: _cfg('JWT_REFRESH_COOKIE', 'refresh_token')
COOKIE_SECURE  = lambda: _cfg('JWT_COOKIE_SECURE', not settings.DEBUG)
COOKIE_SAMESITE = lambda: _cfg('JWT_COOKIE_SAMESITE', 'Lax')
COOKIE_DOMAIN  = lambda: _cfg('JWT_COOKIE_DOMAIN', None)
COOKIE_PATH    = lambda: _cfg('JWT_COOKIE_PATH', '/')


# ─── Token Generation ──────────────────────────────────────────────────────────

def _build_payload(user, lifetime: timedelta, token_type: str) -> dict:
    now = datetime.now(tz=timezone.utc)
    return {
        'user_id': user.pk,
        'username': user.username,
        'role': user.role,
        'email': user.email,
        'type': token_type,
        'iat': now,
        'exp': now + lifetime,
    }


def generate_access_token(user) -> str:
    payload = _build_payload(user, ACCESS_LIFE(), 'access')
    return jwt.encode(payload, SECRET(), algorithm=ALGORITHM())


def generate_refresh_token(user) -> str:
    payload = _build_payload(user, REFRESH_LIFE(), 'refresh')
    return jwt.encode(payload, SECRET(), algorithm=ALGORITHM())


def decode_refresh_token(token: str) -> dict:
    """Décode et valide un refresh token. Lève jwt.InvalidTokenError si invalide."""
    payload = jwt.decode(token, SECRET(), algorithms=[ALGORITHM()])
    if payload.get('type') != 'refresh':
        raise jwt.InvalidTokenError('Token type invalide')
    return payload


# ─── Cookie helpers ────────────────────────────────────────────────────────────

def _cookie_kwargs(max_age: int) -> dict:
    return {
        'max_age': max_age,
        'httponly': True,
        'secure': COOKIE_SECURE(),
        'samesite': COOKIE_SAMESITE(),
        'path': COOKIE_PATH(),
        **(({'domain': COOKIE_DOMAIN()} if COOKIE_DOMAIN() else {})),
    }


def set_auth_cookies(response: HttpResponse, user) -> tuple[str, str]:
    """
    Génère access + refresh tokens et les pose dans les cookies HTTP-only.
    Retourne (access_token, refresh_token) pour usage éventuel dans la réponse.
    """
    access  = generate_access_token(user)
    refresh = generate_refresh_token(user)

    response.set_cookie(
        ACCESS_COOKIE(),
        access,
        **_cookie_kwargs(int(ACCESS_LIFE().total_seconds())),
    )
    response.set_cookie(
        REFRESH_COOKIE(),
        refresh,
        **_cookie_kwargs(int(REFRESH_LIFE().total_seconds())),
    )
    return access, refresh


def delete_auth_cookies(response: HttpResponse) -> None:
    """Supprime les cookies d'authentification (logout)."""
    response.delete_cookie(ACCESS_COOKIE(), path=COOKIE_PATH())
    response.delete_cookie(REFRESH_COOKIE(), path=COOKIE_PATH())


# ─── User info helper ──────────────────────────────────────────────────────────

def get_user_data(user) -> dict:
    """Retourne un dict minimal pour la réponse login/refresh."""
    return {
        'id': user.pk,
        'username': user.username,
        'email': user.email,
        'full_name': user.get_full_name(),
        'role': user.role,
        'is_verified': user.is_verified,
        'photo': user.photo.url if user.photo else None,
    }