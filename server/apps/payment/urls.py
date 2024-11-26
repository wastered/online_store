from django.urls import path
from . import views
from .application import yookassa_webhook

app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
    path('webhook/yookassa', yookassa_webhook.yk_webhook, name='yookassa-webhook'),
]
