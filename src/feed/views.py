from django.views.generic.base import TemplateView

class Index(TemplateView):
    template_name = 'feed/index.html'

index = Index.as_view()

class ManageSubscriptionsView(TemplateView):
    template_name = 'feed/manage_subscriptions.html'

manage_subscriptions_view = ManageSubscriptionsView.as_view()
