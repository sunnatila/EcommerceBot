from django.urls import path
from django.urls import include

from .views import ClickWebhookAPIView, PaymeWebhookView


urlpatterns = [
    path("click/update/", ClickWebhookAPIView.as_view()),
    path("update/", PaymeWebhookView.as_view()),
]

