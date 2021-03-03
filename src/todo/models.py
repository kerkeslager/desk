import uuid

from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    created_utc = models.DateTimeField(auto_now_add=True)
    modified_utc = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=256)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.description


