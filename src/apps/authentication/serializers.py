# src/authentication/serializers.py
"""
Serializers pour l'app authentication
"""
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from core.serializers import TimeStampedSerializer
from .models import User, EleveProfile, EnseignantProfile, ParentProfile, ComptableProfile


# ─── Auth Serializers ─────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion (username ou email + password).
    """
    username = serializers.CharField(
        label=_('Identifiant'),
        help_text=_('Username ou adresse email'),
        write_only=True,
    )
    password = serializers.CharField(
        label=_('Mot de passe'),
        style={'input_type': 'password'},
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Tentative de connexion par username
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )

        # Si échec, tenter par email
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(
                    request=self.context.get('request'),
                    username=user_obj.username,
                    password=password,
                )
            except User.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError(
                _('Identifiant ou mot de passe incorrect.'),
                code='authorization',
            )

        if not user.is_active:
            raise serializers.ValidationError(
                _('Ce compte est désactivé.'),
                code='authorization',
            )

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer pour le changement de mot de passe.
    """
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Ancien mot de passe incorrect.'))
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': _('Les mots de passe ne correspondent pas.')}
            )
        return attrs


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            # Message volontairement vague pour sécurité
            raise serializers.ValidationError(
                _('Aucun compte actif trouvé avec cette adresse email.')
            )
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': _('Les mots de passe ne correspondent pas.')}
            )
        return attrs


# ─── Profile Serializers ──────────────────────────────────────────────────────

class EleveProfileSerializer(TimeStampedSerializer):
    class Meta:
        model = EleveProfile
        fields = [
            'id', 'matricule', 'classe_actuelle',
            'groupe_sanguin', 'allergies', 'notes_medicales',
            'contact_urgence_nom', 'contact_urgence_phone', 'contact_urgence_relation',
            'is_redoublant', 'date_admission',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'matricule', 'created_at', 'updated_at']


class EnseignantProfileSerializer(TimeStampedSerializer):
    matieres_display = serializers.SerializerMethodField()

    class Meta:
        model = EnseignantProfile
        fields = [
            'id', 'numero_cnss', 'diplomes', 'specialite',
            'matieres', 'matieres_display',
            'is_professeur_principal', 'classe_principale',
            'date_embauche', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_matieres_display(self, obj):
        return [{'id': m.id, 'nom': str(m)} for m in obj.matieres.all()]


class ParentProfileSerializer(TimeStampedSerializer):
    class Meta:
        model = ParentProfile
        fields = [
            'id', 'eleves', 'relation', 'profession',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComptableProfileSerializer(TimeStampedSerializer):
    class Meta:
        model = ComptableProfile
        fields = ['id', 'numero_cnss', 'date_embauche', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ─── User Serializers ─────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour l'utilisateur connecté (lecture + mise à jour profil).
    Inclut le profil spécifique selon le rôle.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'full_name',
            'role', 'phone', 'address', 'photo',
            'date_of_birth', 'preferred_language',
            'is_verified', 'is_active',
            'created_at', 'updated_at',
            'profile',
        ]
        read_only_fields = [
            'id', 'username', 'email', 'role',
            'is_verified', 'is_active', 'created_at', 'updated_at',
        ]

    def get_profile(self, obj):
        """Retourne le profil selon le rôle."""
        profile_map = {
            User.RoleChoices.ELEVE: ('eleve_profile', EleveProfileSerializer),
            User.RoleChoices.ENSEIGNANT: ('enseignant_profile', EnseignantProfileSerializer),
            User.RoleChoices.PARENT: ('parent_profile', ParentProfileSerializer),
            User.RoleChoices.COMPTABLE: ('comptable_profile', ComptableProfileSerializer),
        }
        entry = profile_map.get(obj.role)
        if entry:
            attr_name, serializer_class = entry
            profile_obj = getattr(obj, attr_name, None)
            if profile_obj:
                return serializer_class(profile_obj, context=self.context).data
        return None


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer allégé pour les listes d'utilisateurs.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name',
            'role', 'phone', 'photo', 'is_active', 'is_verified',
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'un utilisateur (admin only).
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'address', 'date_of_birth',
            'preferred_language', 'password', 'confirm_password',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError(
                {'confirm_password': _('Les mots de passe ne correspondent pas.')}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour du profil utilisateur (self).
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'address', 'photo', 'date_of_birth', 'preferred_language',
        ]