from django.contrib import admin
from . models import Matiere, Classe, EmploiDuTemps, Note, Presence, Bulletin

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    pass


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    pass

@admin.register(EmploiDuTemps)
class EmploiDuTempsAdmin(admin.ModelAdmin):
    pass

@admin.register(Note)
class Notedmin(admin.ModelAdmin):
    pass

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    pass

@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    pass