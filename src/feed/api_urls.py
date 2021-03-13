from django.urls import path

from . import api_views

urlpatterns = (
    path('item/', api_views.item_list_view),
    path('item/<uuid:identifier>/', api_views.item_detail_view),
    path('subscription/', api_views.subscription_list_view),
    path('subscription/<uuid:identifier>/', api_views.subscription_detail_view),
)
