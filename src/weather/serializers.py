from rest_framework import serializers

from . import models

class RoundingDecimalField(serializers.DecimalField):
    def validate_precision(self, value):
        '''
        Don't return precision errors. This will cause the model to just
        round the value to the stored precision.
        '''
        return value

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = (
            'identifier',
            'name',
            'is_default',
            'zip_code',
            'latitude',
            'longitude',
        )

    latitude = RoundingDecimalField(
        decimal_places=6,
        max_digits=9,
    )
    longitude = RoundingDecimalField(
        decimal_places=6,
        max_digits=9,
    )

    def create(self, validated_data):
        user = self.context['request'].user

        if 'is_default' in validated_data and validated_data['is_default']:
            models.Location.objects.filter(
                user=user,
                is_default=True,
            ).update(is_default=False)

        if models.Location.objects.filter(user=user, is_default=True).count() == 0:
            validated_data['is_default'] = True

        return models.Location.objects.create(
            user=user,
            **validated_data,
        )
