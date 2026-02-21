"""
Validateurs personnalisés
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    """
    Valide un numéro de téléphone guinéen
    Format: +224 XXX XX XX XX ou 622XXXXXX
    """
    pattern = r'^(\+224)?[0-9]{9,12}$'
    if not re.match(pattern, value.replace(' ', '')):
        raise ValidationError(
            _('Numéro de téléphone invalide. Format attendu: +224 XXX XX XX XX')
        )


def validate_matricule(value):
    """
    Valide un matricule élève
    Format: YYYY/NNN/XX (ex: 2026/001/EL)
    """
    pattern = r'^\d{4}/\d{3}/[A-Z]{2}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Matricule invalide. Format attendu: YYYY/NNN/XX (ex: 2026/001/EL)')
        )


def validate_positive(value):
    """
    Valide qu'un nombre est positif
    """
    if value < 0:
        raise ValidationError(_('La valeur doit être positive'))


def validate_note(value):
    """
    Valide qu'une note est entre 0 et 20
    """
    if value < 0 or value > 20:
        raise ValidationError(_('La note doit être entre 0 et 20'))


def validate_file_size(value):
    """
    Valide que la taille d'un fichier ne dépasse pas 5MB
    """
    filesize = value.size
    max_size = 5 * 1024 * 1024  # 5MB
    
    if filesize > max_size:
        raise ValidationError(
            _('La taille du fichier ne doit pas dépasser 5MB')
        )


def validate_image_file_extension(value):
    """
    Valide l'extension d'une image
    """
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            _('Extension de fichier non supportée. Utilisez: jpg, jpeg, png, gif, webp')
        )