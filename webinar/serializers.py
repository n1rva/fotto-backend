from rest_framework import serializers

from .models import Webinar,User, WebinarTag

class WebinarTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarTag
        fields = '__all__'

class WebinarSerializer(serializers.ModelSerializer):

    tags = WebinarTagSerializer(many=True, required=False)

    participants = serializers.SlugRelatedField(
        many=True, 
        queryset=User.objects.all(),
        slug_field='id'
    ) 

    class Meta:
        model = Webinar
        fields = "__all__"

class SimplifiedWebinarSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Webinar
        fields=['title', 'date', 'instructor','wp_group_url']
