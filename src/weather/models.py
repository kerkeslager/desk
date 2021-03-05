import uuid

from django.contrib.auth.models import User
from django.core import validators
from django.db import models

zip_code_validator = validators.RegexValidator(
    r'^\d{5}(\-\d{4})?',
    'Invalid zip code',
)

class Location(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=True, blank=True)
    zip_code = models.CharField(
        blank=True,
        max_length=10,
        null=True,
        validators=(zip_code_validator,),
    )
    latitude = models.DecimalField(
        decimal_places=6,
        max_digits=9,
        validators=(
            validators.MaxValueValidator(90),
            validators.MinValueValidator(-90),
        )
    )
    longitude = models.DecimalField(
        decimal_places=6,
        max_digits=9,
        validators=(
            validators.MaxValueValidator(180),
            validators.MinValueValidator(-180),
        )
    )


    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        if self.name:
            return self.name
        if self.zip_code:
            return self.zip_code
        return '{}, {}'.format(
            self.latitude,
            self.longitude,
        )
