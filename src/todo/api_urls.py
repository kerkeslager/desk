from django.urls import path

from . import api_views

urlpatterns = (
    path('', api_views.task_list_view),
    path('<uuid:identifier>', api_views.task_detail_view),
)
