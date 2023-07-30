from rest_framework import serializers

from .models import Webinar,User


class WebinarSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        many=True, 
        queryset=User.objects.all(),
        slug_field='id'
    ) 
    class Meta:
        model = Webinar
        fields = "__all__"
