"""
Modèles abstraits réutilisables
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Modèle abstrait qui ajoute created_at et updated_at
    À hériter par tous les modèles qui ont besoin de timestamps
    """
    created_at = models.DateTimeField(
        _('date de création'),
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        _('date de modification'),
        auto_now=True
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Modèle abstrait pour soft delete (suppression logique)
    """
    is_deleted = models.BooleanField(
        _('supprimé'),
        default=False,
        db_index=True
    )
    deleted_at = models.DateTimeField(
        _('date de suppression'),
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """Vraie suppression"""
        super().delete()

    def restore(self):
        """Restaurer élément supprimé"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()