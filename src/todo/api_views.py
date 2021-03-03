import datetime

from django.db.models import Q

from rest_framework import viewsets

from . import models, serializers

class TaskViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        q = models.Task.objects.filter(
            Q(is_complete=False) | Q( modified_utc__gt=(datetime.datetime.utcnow().date())),
            user=self.request.user,
        )

        if self.request.method == 'GET':
            allowed_orderings = set((
                'created_utc',
                '-created_utc',
                'description',
                '-description',
                'is_complete',
                '-is_complete',
                'modified_utc',
                '-modified_utc',
            ))

            orderings = [
                ordering
                for ordering in self.request.GET.getlist('order_by')
                if ordering in allowed_orderings
            ]

            if orderings:
                q = q.order_by(*orderings)

        return q

task_list_view = TaskViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

task_detail_view = TaskViewSet.as_view({
    'get': 'retrieve',
    'put': 'partial_update',
    'delete': 'destroy',
})
