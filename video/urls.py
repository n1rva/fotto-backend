from django.urls import path
from . import views

urlpatterns = [
    path('video/', views.get_videos, name='get_all_webinar_records'),
    path('video/create', views.create_video, name='create_webinar_record'),
    path('video/<int:video_id>', views.get_video, name='get_webinar_record'),
    path('video/<int:video_id>/update', views.update_video, name='update_webinar_record'),
    path('video/<int:video_id>/delete', views.delete_video, name='delete_webinar_record'),
    path('video/<int:video_id>/participants', views.get_video_participants, name='get_webinar_record_participants'),
    path('video/user', views.get_user_videos, name='get_user_webinar_records'),
    path('video/user/<int:video_id/delete', views.delete_video_from_user, name='delete_webinar_record_from_user'),
    path('video/user/current', views.get_current_user_videos, name='get_current_users_webinar_record'),
    path('video/file/<int:video_id>/create', views.create_video_file, name='create_video_file'),
    path('video/file/<int:video_file_id>/delete', views.delete_video_file, name='delete_video_file'),
    path('video/file/<int:video_file_id>', views.stream_video, name='stream_video'),

]