from django.contrib import admin
from .models import Demande

@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'qte', 'statuts', 'date_dmd', 'admin')
    list_filter = ('statuts', 'date_dmd')
    search_fields = ('employee__username', 'admin__username')
    list_editable = ('statuts',)
    filter_horizontal = ('materiel',)
