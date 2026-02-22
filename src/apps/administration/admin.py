from django.contrib import admin
from . models import AnneeScolaire, Salle, Inscription, PersonnelNonEnseignant

@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    pass


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonnelNonEnseignant)
class PersonnelNonEnseignantAdmin(admin.ModelAdmin):
    pass

