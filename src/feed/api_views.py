from urllib.parse import urljoin

import bs4
import requests
from rest_framework import mixins, status, views, viewsets
from rest_framework.response import Response

from . import models, serializers

class ItemViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'
    serializer_class = serializers.ItemSerializer

    def get_queryset(self):
        user = self.request.user

        for subscription in models.Subscription.objects.filter(user=user):
            subscription.refresh()

        return models.Item.objects.filter(subscription__user=user)

item_list_view = ItemViewSet.as_view({
    'get': 'list',
})

item_detail_view = ItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'partial_update',
})

class SubscriptionViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.SubscriptionCreateSerializer
        if self.action == 'retrieve':
            return serializers.SubscriptionDetailSerializer
        return serializers.SubscriptionSerializer

    def get_queryset(self):
        return models.Subscription.objects.filter(user=self.request.user)

    def get_object(self):
        instance = super().get_object()

        if self.action == 'retrieve':
            instance.refresh()

        return instance

subscription_list_view = SubscriptionViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

subscription_detail_view = SubscriptionViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy',
})
