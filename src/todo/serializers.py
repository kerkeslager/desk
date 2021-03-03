from rest_framework import serializers

from . import models

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = (
            'identifier',
            'description',
        )

    def create(self, validated_data):
        return models.Task.objects.create(
            user=self.context['request'].user,
            **validated_data,
        )
