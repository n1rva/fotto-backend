from django.urls import path
from . import views

urlpatterns = [
    path('payment/', views.payment_first_step, name='payment_first_step'),
    path('payment/last_step/', views.payment_last_step, name='payment_last_step'),
    path('payment/notification/unread/<str:type>', views.get_unread_notifications, name='get_unread_notifications'),
    path('payment/notification/read/<str:type>', views.get_read_notifications, name='get_read_notifications'),
    path('payment/notification/<int:notification_id>', views.update_notification, name='update_notification'),
    path('payment/deneme/', views.deneme, name='deneme'),
]
