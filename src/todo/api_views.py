from rest_framework import viewsets

from . import models, serializers

class TaskViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        return models.Task.objects.filter(user=self.request.user)

task_list_view = TaskViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

task_detail_view = TaskViewSet.as_view({
    'get': 'retrieve',
    'put': 'partial_update',
    'delete': 'destroy',
})
