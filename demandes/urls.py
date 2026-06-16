from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_gestion_demandes, name='admin_gestion_demandes'),
    path('consulter/', views.consulter_demandes, name='consulter_demandes'),
    path('creer/', views.creer_demande, name='creer_demande'),
    path('traiter/<int:demande_id>/', views.admin_traiter_demande, name='admin_traiter_demande'),
    path('valider/<int:demande_id>/', views.valider_demande, name='valider_demande'),
    path('refuser/<int:demande_id>/', views.refuser_demande, name='refuser_demande'),
    path('supprimer/<int:demande_id>/', views.supprimer_demande, name='supprimer_demande'),
]