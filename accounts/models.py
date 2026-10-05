from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )