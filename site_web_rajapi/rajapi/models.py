from django.db import models

# Create your models here.

from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    """
    Modèle pour stocker les messages de contact reçus via le formulaire
    """
    TYPE_DEMANDE_CHOICES = [
        ('projet', 'Soumettre un projet'),
        ('adhesion', 'Devenir membre'),
        ('partenariat', 'Proposition de partenariat'),
        ('financement', 'Opportunité de financement'),
        ('media', 'Demande média/presse'),
        ('stage', 'Stage/Bénévolat'),
        ('information', 'Demande d\'information'),
        ('autre', 'Autre'),
    ]
    
    PAYS_CHOICES = [
        ('cameroun', 'Cameroun'),
        ('congo', 'Congo'),
        ('rd-congo', 'RD Congo'),
        ('senegal', 'Sénégal'),
        ('cote-ivoire', 'Côte d\'Ivoire'),
        ('ghana', 'Ghana'),
        ('nigeria', 'Nigeria'),
        ('kenya', 'Kenya'),
        ('benin', 'Bénin'),
        ('mauritanie', 'Mauritanie'),
        ('guinee', 'Guinée Conakry'),
        ('afrique-sud', 'Afrique du Sud'),
        ('somalie', 'Somalie'),
        ('egypte', 'Égypte'),
        ('autre', 'Autre pays africain'),
    ]
    
    STATUS_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours de traitement'),
        ('resolu', 'Résolu'),
        ('archive', 'Archivé'),
    ]
    
    # Informations personnelles
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    pays = models.CharField(max_length=50, choices=PAYS_CHOICES, verbose_name="Pays")
    organisation = models.CharField(max_length=200, blank=True, null=True, verbose_name="Organisation")
    
    # Détails du message
    type_demande = models.CharField(max_length=50, choices=TYPE_DEMANDE_CHOICES, verbose_name="Type de demande")
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    
    # Métadonnées
    date_envoi = models.DateTimeField(default=timezone.now, verbose_name="Date d'envoi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nouveau', verbose_name="Statut")
    repondu = models.BooleanField(default=False, verbose_name="Répondu")
    date_reponse = models.DateTimeField(blank=True, null=True, verbose_name="Date de réponse")
    notes_internes = models.TextField(blank=True, null=True, verbose_name="Notes internes")
    
    # Informations techniques
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_envoi']
        
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.sujet} ({self.date_envoi.strftime('%d/%m/%Y')})"
    
    def get_nom_complet(self):
        """Retourne le nom complet"""
        return f"{self.prenom} {self.nom}"
    
    def marquer_comme_resolu(self):
        """Marque le message comme résolu"""
        self.status = 'resolu'
        self.repondu = True
        self.date_reponse = timezone.now()
        self.save()


class NewsletterSubscriber(models.Model):
    """
    Modèle pour les abonnés à la newsletter
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    prenom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Prénom")
    nom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom")
    pays = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pays")
    date_inscription = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    date_desabonnement = models.DateTimeField(blank=True, null=True, verbose_name="Date de désabonnement")
    
    class Meta:
        verbose_name = "Abonné Newsletter"
        verbose_name_plural = "Abonnés Newsletter"
        ordering = ['-date_inscription']
    
    def __str__(self):
        return self.email
    
    def desabonner(self):
        """Désabonne l'utilisateur"""
        self.actif = False
        self.date_desabonnement = timezone.now()
        self.save()