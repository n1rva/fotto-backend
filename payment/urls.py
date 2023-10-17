from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment_first_step, name='payment_first_step'),
    path('payment/last_step/', views.payment_last_step, name='payment_last_step'),
]
