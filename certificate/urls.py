from django.urls import path
from . import views

urlpatterns = [ #endpointleri güncelle
    path('certificate', views.single_certificate_views, name='get_certificate_by_id'),
    path('certificate', views.single_certificate_views, name='create_by_user_id'),
    path('certificate/<int:id>', views.handle_certificate_by_id, name='delete_certificate'),
    path('certificate/<int:id>', views.handle_certificate_by_id, name='update_certificate'),
    path('certificate/user', views.get_current_user_certificates, name='get_current_users_certificate'),
    #path('certificate/get/webinars/', views.getWebinarCertificates, name='get_webinars_certificates'),
    path('certificate/preview', views.preview_certificate, name='create_single_certificate'),
    path('certificate/uniqueid', views.get_certificate_by_unique_id, name='get_certificate_by_unique_id'),
    path('certificate/participants', views.create_certificate_for_participants, name='create_certificates_for_participants'),
    path('certificate/verify', views.verify_certificate, name='verify_certificate'),

]
