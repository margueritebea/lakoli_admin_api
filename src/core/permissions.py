"""
Permissions personnalisées basées sur les rôles
"""
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """
    Permission : utilisateur doit être administrateur
    """
    message = "Vous devez être administrateur pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsEnseignant(permissions.BasePermission):
    """
    Permission : utilisateur doit être enseignant
    """
    message = "Vous devez être enseignant pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ENSEIGNANT'
        )


class IsEleve(permissions.BasePermission):
    """
    Permission : utilisateur doit être élève
    """
    message = "Vous devez être élève pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ELEVE'
        )


class IsParent(permissions.BasePermission):
    """
    Permission : utilisateur doit être parent
    """
    message = "Vous devez être parent pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'PARENT'
        )


class IsComptable(permissions.BasePermission):
    """
    Permission : utilisateur doit être comptable
    """
    message = "Vous devez être comptable pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'COMPTABLE'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission : Admin peut tout faire, autres peuvent seulement lire
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission : propriétaire de l'objet ou admin
    """
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'ADMIN':
            return True
        
        # Vérifier selon le type d'objet
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'eleve'):
            # Pour objets liés à un élève
            if request.user.role == 'ELEVE':
                return obj.eleve.user == request.user
            elif request.user.role == 'PARENT':
                return obj.eleve in request.user.parent_profile.eleves.all()
        
        return False


class IsEnseignantOrAdmin(permissions.BasePermission):
    """
    Permission : enseignant OU admin
    Utile pour saisie de notes, présences, etc.
    """
    message = "Vous devez être enseignant ou administrateur."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['ENSEIGNANT', 'ADMIN']
        )


class IsAdminOrComptable(permissions.BasePermission):
    """
    Permission : admin OU comptable
    Utile pour gestion finances
    """
    message = "Vous devez être administrateur ou comptable."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['ADMIN', 'COMPTABLE']
        )