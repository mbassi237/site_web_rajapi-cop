from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home-page'),
    path('palteforme/', views.plateforme, name='plateforme-page'),
    path('programmes/', views.programmes, name='programmes-page'),
    path('noscontacts/', views.noscontacts, name='noscontacts-page'),
    path('apropos/', views.apropos, name='apropos-page'),
    path('actualites/', views.actualites, name='actualites-page'),
    path('contact/', views.noscontacts_page, name='noscontacts-page'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter-subscribe'),
]