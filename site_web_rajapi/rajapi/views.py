from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'rajapi/home.html')


def apropos(request):
    return render(request, 'rajapi/apropos.html')


def programmes(request):
    return render(request, 'rajapi/programmes.html')


def plateforme(request):
    return render(request, 'rajapi/plateforme.html')


def noscontacts(request):
    return render(request, 'rajapi/noscontacts.html')


def actualites(request):
    return render(request, 'rajapi/actualites.html')





from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ContactMessage, NewsletterSubscriber
from .forms import ContactForm, NewsletterForm
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Donation

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def noscontacts_page(request):
    """
    Vue pour la page de contact avec traitement du formulaire
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Sauvegarder le message
            contact_message = form.save(commit=False)
            contact_message.ip_address = get_client_ip(request)
            contact_message.user_agent = request.META.get('HTTP_USER_AGENT', '')
            contact_message.save()
            
            # Envoyer un email de notification à l'équipe RAJAPI-COP
            try:
                send_notification_email(contact_message)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email de notification: {e}")
            
            # Envoyer un email de confirmation à l'utilisateur
            try:
                send_confirmation_email(contact_message)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email de confirmation: {e}")
            
            # Message de succès
            messages.success(
                request, 
                'Votre message a été envoyé avec succès ! '
                'Notre équipe vous répondra dans les 24-48 heures.'
            )
            
            return redirect('noscontacts-page')
        else:
            # En cas d'erreur de validation
            messages.error(
                request,
                'Une erreur s\'est produite. Veuillez vérifier les informations saisies.'
            )
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'rajapi/noscontacts.html', context)


def send_notification_email(contact_message):
    """
    Envoie un email de notification à l'équipe RAJAPI-COP
    """
    subject = f'Nouveau message de contact - {contact_message.type_demande}'
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2c3e50;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <h2 style="color: #2ecc71;">Nouveau message de contact</h2>
                
                <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #3498db;">Informations du contact</h3>
                    <p><strong>Nom complet:</strong> {contact_message.get_nom_complet()}</p>
                    <p><strong>Email:</strong> {contact_message.email}</p>
                    <p><strong>Téléphone:</strong> {contact_message.telephone or 'Non fourni'}</p>
                    <p><strong>Pays:</strong> {contact_message.get_pays_display()}</p>
                    <p><strong>Organisation:</strong> {contact_message.organisation or 'Non fournie'}</p>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #e67e22;">Détails de la demande</h3>
                    <p><strong>Type de demande:</strong> {contact_message.get_type_demande_display()}</p>
                    <p><strong>Sujet:</strong> {contact_message.sujet}</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Message</h3>
                    <p style="white-space: pre-wrap;">{contact_message.message}</p>
                </div>
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                    <p style="font-size: 12px; color: #7f8c8d;">
                        Message reçu le {contact_message.date_envoi.strftime('%d/%m/%Y à %H:%M')}<br>
                        IP: {contact_message.ip_address}
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    
    plain_message = f"""
    Nouveau message de contact - RAJAPI-COP Africa
    
    Nom: {contact_message.get_nom_complet()}
    Email: {contact_message.email}
    Téléphone: {contact_message.telephone or 'Non fourni'}
    Pays: {contact_message.get_pays_display()}
    Organisation: {contact_message.organisation or 'Non fournie'}
    Type de demande: {contact_message.get_type_demande_display()}
    Sujet: {contact_message.sujet}
    
    Message:
    {contact_message.message}
    
    ---
    Message reçu le {contact_message.date_envoi.strftime('%d/%m/%Y à %H:%M')}
    """
    
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        ['fonder.rajapicop@gmail.com', 'rajapicop.dev.africa@gmail.com']
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_confirmation_email(contact_message):
    """
    Envoie un email de confirmation à l'utilisateur
    """
    subject = 'Votre message a bien été reçu - RAJAPI-COP Africa'
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2c3e50;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2ecc71;">RAJAPI-COP Africa</h1>
                    <p style="color: #7f8c8d;">Réseau des Jeunes Africains pour la Justice Climatique</p>
                </div>
                
                <h2 style="color: #3498db;">Bonjour {contact_message.prenom},</h2>
                
                <p>Nous avons bien reçu votre message concernant : <strong>{contact_message.sujet}</strong></p>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 5px; border-left: 4px solid #2ecc71; margin: 20px 0;">
                    <p style="margin: 0;">
                        <strong>✓ Votre message a été enregistré avec succès</strong><br>
                        Notre équipe s'engage à vous répondre dans les <strong>24 à 48 heures ouvrables</strong>.
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Récapitulatif de votre demande</h3>
                    <p><strong>Type de demande:</strong> {contact_message.get_type_demande_display()}</p>
                    <p><strong>Sujet:</strong> {contact_message.sujet}</p>
                    <p><strong>Date d'envoi:</strong> {contact_message.date_envoi.strftime('%d/%m/%Y à %H:%M')}</p>
                </div>
                
                <p>En attendant notre réponse, n'hésitez pas à :</p>
                <ul>
                    <li>Visiter notre site web : <a href="https://www.rajapi-cop.org">www.rajapi-cop.org</a></li>
                    <li>Suivre nos actualités sur les réseaux sociaux</li>
                    <li>Découvrir nos programmes et initiatives</li>
                </ul>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center;">
                    <p style="color: #7f8c8d; font-size: 12px;">
                        Cet email est envoyé automatiquement, merci de ne pas y répondre.<br>
                        Pour toute question, contactez-nous à : fonder.rajapicop@gmail.com
                    </p>
                    <p style="color: #2ecc71; font-weight: bold; margin-top: 15px;">
                        Promouvoir l'innovation des jeunes pour la justice climatique et la biodiversité
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    
    plain_message = f"""
    Bonjour {contact_message.prenom},
    
    Nous avons bien reçu votre message concernant : {contact_message.sujet}
    
    Notre équipe s'engage à vous répondre dans les 24 à 48 heures ouvrables.
    
    Récapitulatif de votre demande:
    - Type de demande: {contact_message.get_type_demande_display()}
    - Sujet: {contact_message.sujet}
    - Date d'envoi: {contact_message.date_envoi.strftime('%d/%m/%Y à %H:%M')}
    
    Cordialement,
    L'équipe RAJAPI-COP Africa
    
    ---
    www.rajapi-cop.org
    fonder.rajapicop@gmail.com
    """
    
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [contact_message.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    print("=== DEBUG NEWSLETTER ===")
    print("Content-Type :", request.META.get('CONTENT_TYPE', 'absent'))
    print("Raw body :", request.body[:400])

    email = None

    # Tentative 1 : JSON (ce que tu veux supporter)
    if request.META.get('CONTENT_TYPE', '').startswith('application/json'):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            print("JSON parsé → email :", email)
        except json.JSONDecodeError as e:
            print("Erreur JSON decode :", str(e))
            return JsonResponse({
                'success': False,
                'message': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            print("Autre erreur JSON :", str(e))
            return JsonResponse({'success': False, 'message': 'Erreur lors du parsing'}, status=400)

    # Tentative 2 : fallback form-urlencoded (au cas où le js n'a pas changé)
    if email is None:
        email = request.POST.get('email', '').strip()
        print("Fallback POST.get('email') :", email)

    if not email:
        return JsonResponse({
            'success': False,
            'message': 'Adresse email manquante'
        }, status=400)

    # Validation avec le form
    form = NewsletterForm({'email': email})
    if form.is_valid():
        try:
            subscriber = form.save()
            send_welcome_newsletter_email(subscriber)
            return JsonResponse({
                'success': True,
                'message': 'Merci pour votre inscription ! Vous recevrez bientôt nos actualités.'
            })
        except Exception as e:
            print("Erreur sauvegarde / email :", str(e))
            return JsonResponse({
                'success': False,
                'message': 'Inscription enregistrée mais erreur lors de l\'envoi email'
            }, status=200)  # 200 car l'inscription a marché
    else:
        print("Erreurs form :", form.errors.as_json())
        error_msg = form.errors.get('email', ['Erreur de validation'])[0]
        return JsonResponse({
            'success': False,
            'message': str(error_msg)
        }, status=400)

def send_welcome_newsletter_email(subscriber):
    """
    Envoie un email de bienvenue pour la newsletter
    """
    subject = 'Bienvenue dans la communauté RAJAPI-COP !'
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #2c3e50; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 30px 20px;">
                <h1 style="color: #2ecc71; text-align: center; margin-bottom: 30px;">Welcome to RAJAPI-COP Africa! 🌍</h1>
                
                <p>Dear Subscriber,</p>
                
                <p>Thank you very much for subscribing to the RAJAPI-COP Africa newsletter.</p>
                
                <p>By joining our community, you become part of a pan-African youth network, present in around thirty African countries, actively working to deliver innovative, inclusive, and locally driven solutions to challenges related to climate change, biodiversity, desertification, pollution, and social and gender justice.</p>
                
                <p>RAJAPI-COP Africa (<strong>Network of Young Africans Bringing Innovative Projects to the Climate, Biodiversity, and Desertification COPs</strong>) mobilizes and empowers young African leaders to make their voices heard in international decision-making spaces, particularly within the United Nations, and to translate global commitments into concrete action on the ground.</p>
                
                <p>Through this newsletter, you will receive:</p>
                <ul style="padding-left: 20px;">
                    <li>Updates on our key initiatives and activities</li>
                    <li>International opportunities</li>
                    <li>Strategic insights and analyses</li>
                    <li>Actions led by African youth for a sustainable future</li>
                </ul>
                
                <p>We are honored to have you join us and look forward to building together a more just, resilient, and sustainable future for Africa and the world.</p>
                
                <p style="margin-top: 40px;">With our highest regards,</p>
                <p style="font-weight: bold; margin: 5px 0;">The RAJAPI-COP Africa Team</p>
                <p style="color: #7f8c8d; font-size: 15px; margin: 5px 0;">
                    Network of Young Africans Bringing Innovative Projects to the COPs<br>
                    Climate • Biodiversity • Desertification • Social & Gender Justice
                </p>
                
                <div style="text-align: center; margin: 40px 0;">
                    <a href="https://www.rajapi-cop.org" style="background: #2ecc71; color: white; padding: 14px 35px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block; font-size: 16px;">
                        Visit our website
                    </a>
                </div>
                
                <p style="text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 40px;">
                    If you wish to unsubscribe, click <a href="#" style="color: #7f8c8d;">here</a>
                </p>
            </div>
        </body>
    </html>
    """
    
    email = EmailMultiAlternatives(
        subject,
        'Bienvenue dans la communauté RAJAPI-COP !',
        settings.DEFAULT_FROM_EMAIL,
        [subscriber.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    
    
    
    
    
    


import os
from django.conf import settings
from django.http import FileResponse, Http404

def download_document(request, filename):
    # Chemin vers ton dossier static/documents
    documents_dir = os.path.join(settings.BASE_DIR, 'static', 'documents')
    file_path = os.path.join(documents_dir, filename)

    if not os.path.exists(file_path):
        raise Http404("Document introuvable")

    return FileResponse(open(file_path, 'rb'), as_attachment=True)








@require_POST
def donation_submit(request):
    try:
        donation = Donation.objects.create(
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            country=request.POST.get('country'),
            amount=request.POST.get('amount'),
            payment_method=request.POST.get('payment_method'),
            transaction_reference=request.POST.get('transaction_reference', ''),
            purpose=request.POST.get('purpose', ''),
            message=request.POST.get('message', ''),
            anonymous=request.POST.get('anonymous') == 'on',
            newsletter=request.POST.get('newsletter') == 'on'
        )
        
        # Send confirmation email to donor
        send_mail(
            'Thank You for Your Donation to RAJAPI-COP Africa',
            f'Dear {donation.full_name},\n\nThank you for your generous donation of {donation.amount} FCFA...',
            'fonder.rajapicop@gmail.com',
            [donation.email],
            fail_silently=False,
        )
        
        # Send notification to admin
        send_mail(
            f'New Donation: {donation.amount} FCFA',
            f'Name: {donation.full_name}\nAmount: {donation.amount} FCFA\n...',
            'fonder.rajapicop@gmail.com',
            ['fonder.rajapicop@gmail.com'],
            fail_silently=False,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you! We have received your donation notification. You will receive a confirmation email shortly.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again or contact us directly.'
        })