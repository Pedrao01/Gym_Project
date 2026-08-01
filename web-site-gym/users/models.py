from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    phone_number = models.CharField(max_length=11, blank=False, unique=True)

    def __str__(self):
        return f'Username: {self.username} - Email: {self.email}'
