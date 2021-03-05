from rest_framework import serializers

from . import models

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = (
            'identifier',
            'is_read',
        )

class ScrapeSerializer(serializers.Serializer):
    uri = serializers.URLField()

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        models = models.Subscription
        fields = (
            'url',
            'mark_existing_read',
        )

    url = serializers.URLField()
    mark_existing_read = serializers.BooleanField()

    def create(self, **validated_data):
        uri = validated_data['uri']
        mark_existing_read = validated_data['mark_existing_read']

        models.Subscription.objects.create

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        models = models.Subscription
        fields = (
            'identifier',
        )
