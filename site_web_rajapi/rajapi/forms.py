from django import forms
from .models import ContactMessage, NewsletterSubscriber

class ContactForm(forms.ModelForm):
    """
    Formulaire de contact avec validation
    """
    class Meta:
        model = ContactMessage
        fields = ['prenom', 'nom', 'email', 'telephone', 'pays', 
                  'type_demande', 'organisation', 'sujet', 'message']
        widgets = {
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom',
                'required': True
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com',
                'required': True
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+237 XXX XXX XXX'
            }),
            'pays': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'type_demande': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'organisation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de votre organisation'
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Résumez l\'objet de votre message',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez votre demande en détail...',
                'rows': 6,
                'required': True
            }),
        }
    
    def clean_email(self):
        """Validation de l'email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email
    
    def clean_telephone(self):
        """Validation du téléphone"""
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Nettoyer le numéro de téléphone - CORRECTION ICI
            telephone = ''.join(c for c in telephone if c.isdigit() or c in ['+', '-', ' ', '(', ')'])
        return telephone


class NewsletterForm(forms.ModelForm):
    """
    Formulaire d'inscription à la newsletter
    """
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre adresse email',
                'required': True
            })
        }
    
    def clean_email(self):
        """Validation de l'email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Vérifier si l'email existe déjà
            if NewsletterSubscriber.objects.filter(email=email, actif=True).exists():
                raise forms.ValidationError("Cet email est déjà inscrit à notre newsletter.")
        return email