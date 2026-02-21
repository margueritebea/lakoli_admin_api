"""
Signaux Django pour l'app authentication.
- Crée automatiquement le profil spécifique selon le rôle à la création d'un User.
- Log les connexions/déconnexions.
"""
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
import logging

logger = logging.getLogger('authentication')


# ─── Auto-création de profils ─────────────────────────────────────────────────

@receiver(post_save, sender='authentication.User')
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée le profil métier correspondant au rôle dès la création de l'utilisateur.
    Les champs obligatoires sont laissés avec des valeurs par défaut minimales
    pour ne pas bloquer la création ; l'admin ou l'API doit les compléter.
    """
    if not created:
        return

    from .models import (
        User, EleveProfile, EnseignantProfile,
        ParentProfile, ComptableProfile,
    )

    role = instance.role

    if role == User.RoleChoices.ELEVE:
        if not hasattr(instance, 'eleve_profile'):
            from core.utils import generate_matricule
            EleveProfile.objects.create(
                user=instance,
                matricule=generate_matricule(),
                date_admission=timezone.now().date(),
                contact_urgence_nom='',
                contact_urgence_phone='',
                contact_urgence_relation='',
            )
            logger.info('EleveProfile créé pour %s', instance.username)

    elif role == User.RoleChoices.ENSEIGNANT:
        if not hasattr(instance, 'enseignant_profile'):
            EnseignantProfile.objects.create(
                user=instance,
                date_embauche=timezone.now().date(),
            )
            logger.info('EnseignantProfile créé pour %s', instance.username)

    elif role == User.RoleChoices.PARENT:
        if not hasattr(instance, 'parent_profile'):
            ParentProfile.objects.create(
                user=instance,
                relation='AUTRE',
            )
            logger.info('ParentProfile créé pour %s', instance.username)

    elif role == User.RoleChoices.COMPTABLE:
        if not hasattr(instance, 'comptable_profile'):
            ComptableProfile.objects.create(
                user=instance,
                date_embauche=timezone.now().date(),
            )
            logger.info('ComptableProfile créé pour %s', instance.username)


# ─── Logging des connexions ───────────────────────────────────────────────────

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = _get_client_ip(request)
    logger.info('LOGIN  user=%s (role=%s) ip=%s', user.username, user.role, ip)


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        ip = _get_client_ip(request)
        logger.info('LOGOUT user=%s ip=%s', user.username, ip)


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = _get_client_ip(request)
    username = credentials.get('username', '?')
    logger.warning('LOGIN FAILED username=%s ip=%s', username, ip)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_client_ip(request) -> str:
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '?')