"""
Fonctions utilitaires diverses
"""
from django.utils.text import slugify
from datetime import datetime
import random
import string


def generate_unique_code(prefix='', length=8):
    """
    Génère un code unique
    Ex: generate_unique_code('FAC', 6) -> 'FAC-AB12CD'
    """
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=length))
    
    if prefix:
        return f"{prefix}-{code}"
    return code


def generate_matricule(year=None):
    """
    Génère un matricule élève
    Format: YYYY/NNN/EL
    """
    if year is None:
        year = datetime.now().year
    
    # Trouver le dernier numéro
    from apps.authentication.models import EleveProfile
    last_eleve = EleveProfile.objects.filter(
        matricule__startswith=f"{year}/"
    ).order_by('-matricule').first()
    
    if last_eleve:
        # Extraire le numéro
        parts = last_eleve.matricule.split('/')
        number = int(parts[1]) + 1
    else:
        number = 1
    
    return f"{year}/{number:03d}/EL"


def calculate_age(birth_date):
    """
    Calcule l'âge à partir de la date de naissance
    """
    today = datetime.today()
    age = today.year - birth_date.year
    
    # Vérifier si l'anniversaire est passé cette année
    if today.month < birth_date.month or (
        today.month == birth_date.month and today.day < birth_date.day
    ):
        age -= 1
    
    return age


def format_currency(amount, currency='GNF'):
    """
    Formate un montant en devise
    Ex: format_currency(500000, 'GNF') -> '500 000 GNF'
    """
    formatted = f"{amount:,.0f}".replace(',', ' ')
    return f"{formatted} {currency}"


def academic_year_string(start_year=None):
    """
    Génère la chaîne année scolaire
    Ex: academic_year_string(2025) -> '2025-2026'
    """
    if start_year is None:
        # Si on est avant septembre, année précédente
        today = datetime.today()
        start_year = today.year if today.month >= 9 else today.year - 1
    
    return f"{start_year}-{start_year + 1}"


def sanitize_filename(filename):
    """
    Nettoie un nom de fichier pour être safe
    """
    import os
    name, ext = os.path.splitext(filename)
    clean_name = slugify(name)
    return f"{clean_name}{ext}"