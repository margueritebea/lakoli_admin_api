from django.contrib import admin

from finances.models import FraisScolaire, Facture, Paiement, RapportFinancier


@admin.register(FraisScolaire)
class FraisScolaireAdmin(admin.ModelAdmin):
    pass


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    pass


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    pass


@admin.register(RapportFinancier)
class RapportFinancierAdmin(admin.ModelAdmin):
    pass