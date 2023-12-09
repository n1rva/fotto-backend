from django.urls import path
from . import views

urlpatterns = [
    path('webinar', views.get_all_webinars, name='get_all_webinars'),
    path('webinar/search/<str:search_query>', views.search_webinar, name='search_webinar'),
    path('webinar/filters', views.get_all_webinar_filters, name='get_all_webinar_filters'),
    path('webinar/filters/<str:tag_names>', views.webinars_by_tag, name='webinars_by_tag'),
    path('webinar/filters/search/<str:search_query>/', views.search_filters, name='search_tags'),
    path('webinar/create', views.create_webinar, name='create_webinar'),
    path('webinar/<int:webinar_id>', views.get_webinar, name='get_webinar'),
    path('webinar/<slug:webinar_slug>/slug', views.get_webinar_by_slug, name='get_webinar_by_slug'),
    path('webinar/<int:webinar_id>/participants', views.get_webinar_participants, name='get_participants'), #
    path('webinar/<int:webinar_id>/update', views.update_webinar, name='update_webinar'),
    path('webinar/<int:webinar_id>/delete', views.delete_webinar, name='delete_webinar'),
    path('webinar/<int:webinar_id>/user', views.delete_webinar_from_user, name='delete_webinar_from_user'),
    path('webinar/<int:webinar_id>/check', views.check_if_user_has_webinar, name='check_if_user_has_webinar'),
    path('webinar/user', views.get_user_webinars, name='get_user_webinars'),
    path('webinar/current/active', views.get_current_user_active_webinars, name='get_current_user_webinars'),
    path('webinar/current/expired', views.get_current_user_expired_webinars, name='get_current_user_expired_webinars'),
]
