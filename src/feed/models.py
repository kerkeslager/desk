import uuid

from django.contrib.auth.models import User
from django.db import models

class Item(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    is_read = models.BooleanField(default=False)
    title = models.CharField(blank=True, max_length=256, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.CharField(blank=True, max_length=256, null=True)

class Subscription(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed_uri = models.URLField()
    title = models.CharField(blank=True, max_length=256, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.CharField(blank=True, max_length=256, null=True)
