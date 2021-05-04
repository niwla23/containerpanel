from django.db import models
from django.contrib.auth.models import User


class Container(models.Model):
    container_id = models.UUIDField(primary_key=True)
    description = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    allowed_users = models.ManyToManyField(User, verbose_name="Users allowed to manage this container")
