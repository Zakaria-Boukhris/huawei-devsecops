from django.contrib import admin
from .models import Site, Materiel

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'location')
    search_fields = ('nom', 'location')

@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'qte_dispo', 'description')
    list_filter = ('qte_dispo',)
    search_fields = ('nom', 'description')
    list_editable = ('qte_dispo',)
