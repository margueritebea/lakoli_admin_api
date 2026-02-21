"""
Backend d'authentification personnalisé.
Permet la connexion par email OU username.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Backend qui accepte email ou username comme identifiant.
    À ajouter dans settings.AUTHENTICATION_BACKENDS.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Chercher par username d'abord
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Tenter par email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                # Exécuter un hash inutile pour mitiger le timing attack
                User().set_password(password)
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None