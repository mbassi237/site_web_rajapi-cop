from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, NewsletterSubscriber

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['get_nom_complet', 'email', 'type_demande', 'pays', 'status', 'repondu', 'date_envoi']
    list_filter = ['status', 'type_demande', 'pays', 'repondu', 'date_envoi']
    search_fields = ['prenom', 'nom', 'email', 'sujet', 'message', 'organisation']
    readonly_fields = ['date_envoi', 'ip_address', 'user_agent']
    date_hierarchy = 'date_envoi'
    
    fieldsets = (
        ('Informations du contact', {
            'fields': ('prenom', 'nom', 'email', 'telephone', 'pays', 'organisation')
        }),
        ('Détails de la demande', {
            'fields': ('type_demande', 'sujet', 'message')
        }),
        ('Gestion', {
            'fields': ('status', 'repondu', 'date_reponse', 'notes_internes')
        }),
        ('Informations techniques', {
            'fields': ('date_envoi', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marquer_comme_resolu', 'marquer_comme_en_cours']
    
    def marquer_comme_resolu(self, request, queryset):
        updated = queryset.update(status='resolu', repondu=True)
        self.message_user(request, f'{updated} message(s) marqué(s) comme résolu(s).')
    marquer_comme_resolu.short_description = "Marquer comme résolu"
    
    def marquer_comme_en_cours(self, request, queryset):
        updated = queryset.update(status='en_cours')
        self.message_user(request, f'{updated} message(s) marqué(s) comme en cours.')
    marquer_comme_en_cours.short_description = "Marquer comme en cours"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'prenom', 'nom', 'pays', 'actif', 'date_inscription']
    list_filter = ['actif', 'pays', 'date_inscription']
    search_fields = ['email', 'prenom', 'nom']
    readonly_fields = ['date_inscription', 'date_desabonnement']
    date_hierarchy = 'date_inscription'
    
    actions = ['activer_abonnement', 'desactiver_abonnement']
    
    def activer_abonnement(self, request, queryset):
        updated = queryset.update(actif=True, date_desabonnement=None)
        self.message_user(request, f'{updated} abonnement(s) activé(s).')
    activer_abonnement.short_description = "Activer l'abonnement"
    
    def desactiver_abonnement(self, request, queryset):
        for subscriber in queryset:
            subscriber.desabonner()
        self.message_user(request, f'{queryset.count()} abonnement(s) désactivé(s).')
    desactiver_abonnement.short_description = "Désactiver l'abonnement"