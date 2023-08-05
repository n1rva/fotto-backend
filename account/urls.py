from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('user/', views.getUser, name='get_user'),
    path('user/<str:pk>/', views.getUserById, name='get_user_by_id'),
    path('user/update/info', views.update_profile, name='update_user'),
    path('user/update/pass', views.update_password, name='update_pass'),
    path('user/search', views.userSearch, name='user_search'),
]
