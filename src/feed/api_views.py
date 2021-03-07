from urllib.parse import urljoin

import bs4
import requests
from rest_framework import mixins, status, views, viewsets
from rest_framework.response import Response

from core import cache

from . import models, serializers

class ItemViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'
    serializer_class = serializers.ItemSerializer

    def get_queryset(self):
        return models.Item.objects.filter(user=self.request.user)

item_list_view = ItemViewSet.as_view({
    'get': 'list',
})

item_detail_view = ItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'partial_update',
})

class ScrapeView(views.APIView):
    def get(self, request):
        serializer = serializers.ScrapeSerializer(
            data=request.query_params,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        page_uri = serializer.validated_data['uri']

        response = requests.get(page_uri)

        assert response.status_code == 200

        page_content = bs4.BeautifulSoup(response.content, 'html.parser')


        rss_root = page_content.find('rss')

        if rss_root:
            channel = rss_root.channel

            return Response({
                'feeds': [
                    {
                        'uri': page_uri,
                        'title': channel.title.text,
                        'description': channel.description.text,
                    }
                ],
            })

        page_links = page_content.find_all('link', type='application/rss+xml')

        feeds = [
            {
                'uri': urljoin(page_uri, l.attrs['href']),
                'title': l.attrs.get('title'),
            }
            for l in page_links
            if l.attrs.get('href')
        ]

        return Response({
            'feeds': feeds,
        })

scrape_view = ScrapeView.as_view()

class SubscriptionViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'
    serializer_class = serializers.SubscriptionSerializer

    def get_queryset(self):
        return models.Subscription.objects.filter(user=self.request.user)

subscription_list_view = SubscriptionViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

subscription_detail_view = SubscriptionViewSet.as_view({
    'get': 'retrieve',
    'put': 'partial_update',
    'delete': 'destroy',
})

class SubscribeView(views.APIView, mixins.CreateModelMixin):
    serializer_class = serializers.SubscribeSerializer

subscribe_view = SubscribeView.as_view()
