from django.db import models

class Site(models.Model):
    nom = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Materiel(models.Model):
    STATUT_VALIDATION_CHOICES = [
        ('EN_ATTENTE', 'En attente de validation'),
        ('VALIDE', 'Validé'),
        ('REJETE', 'Rejeté'),
    ]

    nom = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True, null=True)
    qte_dispo = models.IntegerField()
    description = models.TextField()
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    statut_validation = models.CharField(
        max_length=20,
        choices=STATUT_VALIDATION_CHOICES,
        default='EN_ATTENTE',
        help_text="Statut de validation du matériel"
    )
    date_validation = models.DateTimeField(null=True, blank=True, help_text="Date de validation/rejet")

    def __str__(self):
        return self.nom
