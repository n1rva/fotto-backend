from rest_framework import serializers

from .models import Video, VideoFile, VideoTags


class VideoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTags
        fields = '__all__'

class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    tags = VideoTagSerializer(many=True, required=False)

    class Meta:
        model = Video
        fields = "__all__"