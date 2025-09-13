from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, Technicien


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration des utilisateurs personnalisés"""
    
    # Champs affichés dans la liste
    list_display = (
        'email', 
        'username', 
        'first_name', 
        'last_name', 
        'is_active', 
        'is_staff', 
        'is_superuser',
        'date_joined',
        'has_technicien_profile'
    )
    
    # Champs pour filtrer
    list_filter = (
        'is_active', 
        'is_staff', 
        'is_superuser', 
        'date_joined',
        'last_login'
    )
    
    # Champs de recherche
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    
    # Champs pour le formulaire d'ajout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'username', 
                'first_name', 
                'last_name', 
                'password1', 
                'password2'
            ),
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_active')
        }),
    )
    
    # Ordre par défaut
    ordering = ('email',)
    
    def has_technicien_profile(self, obj):
        """Vérifie si l'utilisateur a un profil technicien"""
        return hasattr(obj, 'technicien_profile')
    has_technicien_profile.short_description = 'Profil Technicien'
    has_technicien_profile.boolean = True


class TechnicienInline(admin.StackedInline):
    """Inline pour afficher le profil technicien dans l'admin User"""
    model = Technicien
    extra = 0
    can_delete = True
    verbose_name_plural = "Profil Technicien"
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'telephone', 'adresse', 'photo')
        }),
        ('Informations professionnelles', {
            'fields': ('experience', 'disponibilite')
        }),
    )


@admin.register(Technicien)
class TechnicienAdmin(admin.ModelAdmin):
    """Administration des techniciens"""
    
    # Champs affichés dans la liste
    list_display = (
        'nom_complet',
        'user_email',
        'telephone',
        'experience',
        'disponibilite',
        'photo_thumbnail',
        'created_at'
    )
    
    # Champs pour filtrer
    list_filter = (
        'disponibilite',
        'experience',
        'created_at',
        'updated_at'
    )
    
    # Champs de recherche
    search_fields = (
        'nom',
        'prenom',
        'user__email',
        'user__username',
        'telephone'
    )
    
    # Champs modifiables directement depuis la liste
    list_editable = ('disponibilite',)
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'telephone', 'adresse', 'photo')
        }),
        ('Informations professionnelles', {
            'fields': ('experience', 'disponibilite')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('created_at', 'updated_at')
    
    # Ordre par défaut
    ordering = ('nom', 'prenom')
    
    # Actions personnalisées
    actions = ['marquer_disponible', 'marquer_indisponible']
    
    def nom_complet(self, obj):
        """Retourne le nom complet du technicien"""
        return f"{obj.prenom or ''} {obj.nom or ''}".strip() or "Non défini"
    nom_complet.short_description = 'Nom complet'
    nom_complet.admin_order_field = 'nom'
    
    def user_email(self, obj):
        """Retourne l'email de l'utilisateur lié"""
        return obj.user.email
    user_email.short_description = 'Email utilisateur'
    user_email.admin_order_field = 'user__email'
    
    def disponibilite_badge(self, obj):
        """Affiche un badge coloré pour la disponibilité"""
        if obj.disponibilite:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">'
                'DISPONIBLE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">'
                'INDISPONIBLE</span>'
            )
    disponibilite_badge.short_description = 'Disponibilité'
    disponibilite_badge.admin_order_field = 'disponibilite'
    
    def photo_thumbnail(self, obj):
        """Affiche une miniature de la photo"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; '
                'border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background-color: #ddd; '
            'border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; font-size: 12px;">Pas de photo</div>'
        )
    photo_thumbnail.short_description = 'Photo'
    
    def marquer_disponible(self, request, queryset):
        """Action pour marquer les techniciens sélectionnés comme disponibles"""
        updated = queryset.update(disponibilite=True)
        self.message_user(
            request,
            f'{updated} technicien(s) marqué(s) comme disponible(s).'
        )
    marquer_disponible.short_description = "Marquer comme disponible"
    
    def marquer_indisponible(self, request, queryset):
        """Action pour marquer les techniciens sélectionnés comme indisponibles"""
        updated = queryset.update(disponibilite=False)
        self.message_user(
            request,
            f'{updated} technicien(s) marqué(s) comme indisponible(s).'
        )
    marquer_indisponible.short_description = "Marquer comme indisponible"
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related"""
        return super().get_queryset(request).select_related('user')


# Configuration alternative : Ajouter TechnicienInline à UserAdmin
# Décommentez les lignes suivantes si vous voulez gérer le profil technicien
# directement depuis l'interface utilisateur

# # Réenregistrer UserAdmin avec l'inline
# admin.site.unregister(User)
# 
# @admin.register(User)
# class UserWithTechnicienAdmin(UserAdmin):
#     inlines = [TechnicienInline]


# Personnalisation du titre et de l'en-tête de l'admin
admin.site.site_header = "Administration du Système"
admin.site.site_title = "Admin"
admin.site.index_title = "Panneau d'administration"