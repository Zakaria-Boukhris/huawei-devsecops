from django.contrib.auth.models import AbstractUser
from django.db import models
from materiel.models import Site

class User(AbstractUser):
    nom = models.CharField(max_length=255, blank=True)
    prenom = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    is_employee = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL)
    affected_site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def login(self):
        
        pass

    def logout(self):
        
        pass

    def __str__(self):
        return self.username

class Employee(User):
    class Meta:
        proxy = True

class Admin(User):
    class Meta:
        proxy = True
