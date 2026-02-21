"""
Gestion d'exceptions personnalisées
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions personnalisé pour formater toutes les erreurs
    de manière cohérente
    """
    # Appeler le gestionnaire par défaut d'abord
    response = exception_handler(exc, context)
    
    # Si c'est une exception DRF standard
    if response is not None:
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': 'Une erreur est survenue',
            'details': response.data
        }
        response.data = custom_response_data
        return response
    
    # Gérer les exceptions Django spécifiques
    if isinstance(exc, DjangoValidationError):
        return Response({
            'error': True,
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': 'Erreur de validation',
            'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, Http404):
        return Response({
            'error': True,
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': 'Ressource introuvable',
            'details': str(exc)
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Erreur serveur générique
    return Response({
        'error': True,
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'message': 'Erreur serveur interne',
        'details': str(exc)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomAPIException(Exception):
    """
    Exception personnalisée pour l'API
    """
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)