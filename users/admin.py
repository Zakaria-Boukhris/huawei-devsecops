from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'nom', 'prenom', 'is_employee', 'is_admin', 'site')
    list_filter = ('is_employee', 'is_admin', 'site')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('nom', 'prenom', 'is_employee', 'is_admin', 'site', 'affected_site')
        }),
    )
