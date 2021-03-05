import uuid

from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    is_read = models.BooleanField(default=False)

class Subscription(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    canonical_url = models.UrlField()
    feed_uri = models.URLField()

