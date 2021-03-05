from django.urls import path

from . import api_views

urlpatterns = (
    path('item/', api_views.item_list_view),
    path('item/<uuid:identifier>/', api_views.item_detail_view),
    path('scrape/', api_views.scrape_view),
    path('subscribe/', api_views.subscribe_view),
    path('subscription/', api_views.subscription_list_view),
    path('subscription/<uuid:identifier>/', api_views.subscription_list_view),
)
