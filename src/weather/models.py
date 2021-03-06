import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.db.models import signals
from django.dispatch import receiver

zip_code_validator = validators.RegexValidator(
    r'^\d{5}(\-\d{4})?',
    'Invalid zip code',
)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_location = models.ForeignKey(
        'Location',
        on_delete=models.PROTECT,
    )

    # TODO Validate that default location belongs to user

class Location(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

    @property
    def is_default(self):
        profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'default_location': Location.objects.filter(user=self.user)[0]
            }
        )

        return profile.default_location == self

    @is_default.setter
    def is_default(self, value):
        if not value:
            raise Exception(
                'Cannot use this helper to remove a default location. '
                'To set is_default to false, set another location as default '
                'location instead.'
            )

        profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'default_location': self
            }
        )

        if profile.default_location != self:
            profile.default_location = self
            profile.save()
