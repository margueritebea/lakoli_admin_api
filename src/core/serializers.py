"""
Serializers de base réutilisables
"""
from rest_framework import serializers


class TimeStampedSerializer(serializers.ModelSerializer):
    """
    Serializer de base avec timestamps en lecture seule
    """
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Serializer minimal pour User (pour relations FK)
    Utilisé quand on veut juste afficher nom/email sans tous les détails
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'photo'
        ]
        read_only_fields = fields


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer qui permet de choisir les champs à retourner
    Usage: GET /api/users/?fields=id,username,email
    """
    def __init__(self, *args, **kwargs):
        # Récupérer paramètre 'fields' de la requête
        fields = kwargs.pop('fields', None)
        
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            # Filtrer les champs
            allowed = set(fields.split(','))
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)