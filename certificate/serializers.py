from rest_framework import serializers

from .models import Certificate,Webinar


class WebinarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webinar
        fields = ('title', 'date', 'instructor')

class CertificateSerializer(serializers.ModelSerializer):
    webinar = WebinarSerializer() 

    class Meta:
        model = Certificate
        fields = '__all__'