from rest_framework import serializers

from . import models

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = (
            'identifier',
            'is_read',
            'link',
            'title',
            'author',
            'description',
            'content',
        )
        read_only_fields = (
            'identifier',
            'link',
            'title',
            'author',
            'description',
            'content',
        )

    def run_validation(self, data=None):
        if data == None:
            return super().run_validation()

        if not data:
            return super().run_validation(data)

        read_only_errors = {
            key: 'This field is read-only'
            for key in data
            if self.fields.get(key) and self.fields[key].read_only
        }

        if read_only_errors:
            raise serializers.ValidationError(read_only_errors)

        return super().run_validation(data)

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = (
            'identifier',
            'feed_uri',
            'link',
            'title',
            'description',
        )


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = (
            'feed_uri',
            'mark_read',
        )

    mark_read = serializers.BooleanField(default=False)

    def create(self, validated_data):
        user = self.context['request'].user
        mark_read = validated_data.pop('mark_read')
        instance = models.Subscription.objects.create(
            user=user,
            **validated_data,
        )
        instance.refresh()

        if mark_read:
            instance.items.update(is_read=True)

        return instance

class SubscriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = (
            'identifier',
            'feed_uri',
            'title',
            'link',
            'description',
            'items',
        )

    items = ItemSerializer(many=True)
