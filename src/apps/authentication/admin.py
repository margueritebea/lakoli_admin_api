# src/apps/authentication/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, EleveProfile, EnseignantProfile, ParentProfile, ComptableProfile


# ─── Inlines ──────────────────────────────────────────────────────────────────

class EleveProfileInline(admin.StackedInline):
    model = EleveProfile
    can_delete = False
    verbose_name_plural = _('Profil Élève')
    fk_name = 'user'
    extra = 0
    fields = (
        'matricule', 'classe_actuelle', 'date_admission', 'is_redoublant',
        'groupe_sanguin', 'allergies', 'notes_medicales',
        'contact_urgence_nom', 'contact_urgence_phone', 'contact_urgence_relation',
    )


class EnseignantProfileInline(admin.StackedInline):
    model = EnseignantProfile
    can_delete = False
    verbose_name_plural = _('Profil Enseignant')
    fk_name = 'user'
    extra = 0
    filter_horizontal = ('matieres',)
    fields = (
        'specialite', 'diplomes', 'numero_cnss', 'date_embauche',
        'matieres', 'is_professeur_principal', 'classe_principale',
    )


class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    can_delete = False
    verbose_name_plural = _('Profil Parent')
    fk_name = 'user'
    extra = 0
    filter_horizontal = ('eleves',)


class ComptableProfileInline(admin.StackedInline):
    model = ComptableProfile
    can_delete = False
    verbose_name_plural = _('Profil Comptable')
    fk_name = 'user'
    extra = 0


ROLE_INLINE_MAP = {
    User.RoleChoices.ELEVE: EleveProfileInline,
    User.RoleChoices.ENSEIGNANT: EnseignantProfileInline,
    User.RoleChoices.PARENT: ParentProfileInline,
    User.RoleChoices.COMPTABLE: ComptableProfileInline,
}


# ─── User Admin ───────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'get_full_name', 'role',
        'is_active', 'is_verified', 'created_at',
    )
    list_filter = ('role', 'is_active', 'is_verified', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {
            'fields': (
                'first_name', 'last_name', 'email',
                'phone', 'address', 'photo', 'date_of_birth',
                'preferred_language',
            )
        }),
        (_('Rôle & statut'), {
            'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser')
        }),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions'),
        }),
        (_('Dates'), {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'role', 'password1', 'password2',
            ),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj and obj.role in ROLE_INLINE_MAP:
            return [ROLE_INLINE_MAP[obj.role]]
        return []

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Nom complet')
    get_full_name.admin_order_field = 'last_name'


# ─── Profile Admins ───────────────────────────────────────────────────────────

@admin.register(EleveProfile)
class EleveProfileAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'get_full_name', 'classe_actuelle', 'is_redoublant', 'date_admission')
    list_filter = ('is_redoublant', 'groupe_sanguin', 'classe_actuelle')
    search_fields = ('matricule', 'user__first_name', 'user__last_name', 'user__email')
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Compte'), {'fields': ('user', 'matricule', 'classe_actuelle', 'date_admission', 'is_redoublant')}),
        (_('Médical'), {
            'classes': ('collapse',),
            'fields': ('groupe_sanguin', 'allergies', 'notes_medicales'),
        }),
        (_('Contact urgence'), {
            'fields': ('contact_urgence_nom', 'contact_urgence_phone', 'contact_urgence_relation'),
        }),
        (_('Horodatage'), {'classes': ('collapse',), 'fields': ('created_at', 'updated_at')}),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Nom complet')
    get_full_name.admin_order_field = 'user__last_name'


@admin.register(EnseignantProfile)
class EnseignantProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialite', 'is_professeur_principal', 'classe_principale', 'date_embauche')
    list_filter = ('is_professeur_principal',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'specialite')
    autocomplete_fields = ('user',)
    filter_horizontal = ('matieres',)
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Nom complet')
    get_full_name.admin_order_field = 'user__last_name'


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'relation', 'profession')
    list_filter = ('relation',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    autocomplete_fields = ('user',)
    filter_horizontal = ('eleves',)
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Nom complet')


@admin.register(ComptableProfile)
class ComptableProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'numero_cnss', 'date_embauche')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'numero_cnss')
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = _('Nom complet')