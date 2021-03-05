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
        return models.Location.objects.create(
            user=self.context['request'].user,
            **validated_data,
        )
