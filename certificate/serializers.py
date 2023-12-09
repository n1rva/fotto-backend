from rest_framework import serializers

from .models import Certificate,Webinar,Video


class WebinarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webinar
        fields = ('title', 'date', 'instructor')
        
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webinar
        fields = ('title', 'date', 'instructor')

class CertificateSerializer(serializers.ModelSerializer):
    webinar = WebinarSerializer() 
    video = VideoSerializer() 

    class Meta:
        model = Certificate
        fields = '__all__'
        
class SimplifiedWebinarCertificateSerializer(serializers.ModelSerializer):
    webinar = WebinarSerializer() 
    class Meta:
        model = Certificate
        fields = ['webinar', 'unique_id']
        
class SimplifiedVideoCertificateSerializer(serializers.ModelSerializer):
    video = VideoSerializer() 
    class Meta:
        model = Certificate
        fields = ['video', 'unique_id']