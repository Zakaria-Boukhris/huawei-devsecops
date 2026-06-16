from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_gestion_materiels, name='admin_gestion_materiels'),
    path('gestion/', views.gestion_stock, name='gestion_stock'),
    path('liste/', views.liste_materiels_employe, name='liste_materiels_employe'),
    path('voir/', views.voir_materiels, name='voir_materiels'),
    path('ajouter/', views.ajouter_materiel, name='ajouter_materiel'),
    path('modifier/<int:materiel_id>/', views.modifier_materiel, name='modifier_materiel'),
    path('valider/<int:materiel_id>/', views.valider_materiel, name='valider_materiel'),
    path('supprimer/<int:materiel_id>/', views.supprimer_materiel, name='supprimer_materiel'),
]