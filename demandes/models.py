from django.db import models
from django.contrib.auth import get_user_model
from materiel.models import Materiel, Site

User = get_user_model()

class Demande(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDEE', 'Validée'),
        ('REFUSEE', 'Refusée'),
    ]

    qte = models.IntegerField()
    description = models.TextField(help_text="Description détaillée de la demande")
    statuts = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    date_dmd = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True, null=True)

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_employee')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_admin')
    materiel = models.ManyToManyField(Materiel, related_name='demandes')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, help_text="Site de livraison")

    def __str__(self):
        return f"Demande {self.id} - {self.statuts}"
