from django.urls import path
from . import views

urlpatterns = [
    path('webinar', views.get_all_webinars, name='get_all_webinars'),
    path('webinar/create', views.create_webinar, name='create_webinar'),
    path('webinar/<int:webinar_id>', views.get_webinar, name='get_webinar'),
    path('webinar/<int:webinar_id>/participants', views.get_webinar_participants, name='get_participants'), #
    path('webinar/<int:webinar_id>/update', views.update_webinar, name='update_webinar'),
    path('webinar/<int:webinar_id>/delete', views.delete_webinar, name='delete_webinar'),
    path('webinar/<int:webinar_id>/user', views.delete_webinar_from_user, name='delete_webinar_from_user'),
    path('webinar/user', views.get_user_webinars, name='get_user_webinars'),
    path('webinar/current', views.get_current_user_webinars, name='get_current_user_webinars'),
]
