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

    is_default = serializers.BooleanField(required=False)
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

        set_default = validated_data.pop('is_default',False)

        result = models.Location.objects.create(
            user=user,
            **validated_data,
        )

        if set_default:
            result.is_default = True

        return result

    def update(self, instance, validated_data):
        set_default = validated_data.pop('is_default',False)

        result = super().update(instance, validated_data)

        if set_default:
            result.is_default = True

        return result
