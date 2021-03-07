from django.urls import path

from . import views

urlpatterns = (
    path('', views.index),
    path('subscriptions/manage/', views.manage_subscriptions_view),
)
