import mimetypes
import os
import re
from wsgiref.util import FileWrapper
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.conf import settings
from mimetypes import guess_type

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated

from account.serializers import UserSerializer

from .serializers import VideoFileSerializer, VideoSerializer

from .models import Video, VideoFile

from django.utils.http import http_date

from django.core.exceptions import ObjectDoesNotExist

from ranged_response import RangedFileResponse

# Create your views here.

@api_view(['POST']) 
@permission_classes([IsAdminUser]) 
def create_video(request):

    data = request.data
    data['participants'] = request.user.id

    serializer = VideoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success':True,'message': 'Webinar kaydı başarıyla oluşturuldu.', 'video':serializer.data}, status=status.HTTP_201_CREATED)  
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser]) 
def update_video(request, video_id):
    
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        
    serializer = VideoSerializer(video, data=request.data, partial=True)  
   
    if serializer.is_valid():
        serializer.save()
        return Response({'success':True,'message': 'Webinar kaydı başarıyla güncellendi.', 'video':serializer.data},status=status.HTTP_200_OK)

    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def delete_video(request,video_id):
    try:
        video = Video.objects.get(id=video_id) # exception yakala
        
        video.delete()
        
        return Response({'success':True, 'message':'Webinar kaydı başarıyla silindi.'},status=status.HTTP_204_NO_CONTENT)     
    
    except Video.DoesNotExist:  
        
         return Response({'error':'Webinar kaydı bulunamadı.'},status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_video(request,video_id):
   try:
        video = Video.objects.get(id=video_id)  
        serializer = VideoSerializer(video)

        try:
            video_file = video.videofile
            video_file_serializer = VideoFileSerializer(video_file)
            response_data = {
                'success': True,
                'video': serializer.data,
                'video_file': video_file_serializer.data
            }
        except VideoFile.DoesNotExist:
            response_data = {
                'success': True,
                'video': serializer.data,
                'video_file': None
            }

        return Response(response_data,status=status.HTTP_200_OK)     

   
   except Video.DoesNotExist:
        return Response({'error':'Webinar kaydı bulunamadı.'},status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_videos(req):
   all_videos = Video.objects.all()

   serializer = VideoSerializer(all_videos, many=True) 
   
   return Response({'success':True,'videos':serializer.data},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_videos(request):

  user_id = request.query_params.get('user_id')

  if not user_id:
    return Response({"error": "User ID parameter is required"}, status=400)
  
  try:
    videos = Video.objects.filter(participants=user_id)
    
    if not videos:
      return Response({"error": "Kullanıcı için webinar kaydı bulunamadı."}, status=404)

    serializer = VideoSerializer(videos, many=True)
    return Response({'success':True, 'videos':serializer.data}, status=200)

  except ObjectDoesNotExist:
    return Response({"error": "Kullanıcı bulunamadı."}, status=404)

  except Exception as e:
    return Response({"error": str(e)}, status=500)
  

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_current_user_videos(req):
   videos = Video.objects.filter(participants=req.user.id)

   data = []

   for video in videos:
        video_data = VideoSerializer(video).data

        try:
            video_file = VideoFile.objects.get(video=video)
            file_data = VideoFileSerializer(video_file).data
            video_data['file']= file_data

        except VideoFile.DoesNotExist:
            pass

        data.append(video_data)

   
   return Response({'success':True,'videos':data},status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def get_video_participants(req,video_id):
    try:
        video = Video.objects.get(id=video_id)
        participants = video.participants.all()
        serializer = UserSerializer(participants, many=True)
        return Response({'success':True, 'participants':serializer.data})
    
    except Video.DoesNotExist:
        return Response({'success':False,'message': 'Webinar kaydı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def delete_video_from_user(req, video_id):

    args= {'id': video_id ,'participants' : req.data.get('user_id') }

    try:
        video = Video.objects.get(**args)
    except Video.DoesNotExist:
        return Response({'success':False, 'message': 'Webinar kaydı kullanıcı için bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

    video.participants.remove(req.user)

    return Response({'success':True,'message': 'Webinar kaydı kullanıcıdan başarıyla silindi.'},status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser]) 
def create_video_file(request, video_id):
    try:
        video = Video.objects.get(id=video_id) 
    except Video.DoesNotExist:
        return Response({'error': 'Webinar kaydı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
       
    if VideoFile.objects.filter(video=video).exists():
        return Response({'success':False, 'message': 'Webinar kaydı halihazırda videoya sahip.'})
            
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'Dosya yüklenemedi.'}, status=status.HTTP_400_BAD_REQUEST)
      
    video_file = VideoFile(video=video, file=file)
    video_file.save()
   
    serializer = VideoFileSerializer(video_file, many=False)   
    return Response({'success': True, 'message': 'Webinar kaydı başarıyla yüklendi.', 'video_file': serializer.data})   

@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def delete_video_file(request, video_file_id):
    try:
        video_file = VideoFile.objects.get(id=video_file_id)
    except VideoFile.DoesNotExist:
        return Response({'error': 'Webinar kaydı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

    video_file.file.delete()
    video_file.delete()

    return Response({'success': True, 'message': 'Webinar kaydı başarıyla silindi.'})

@api_view(['GET'])  
def stream_video(request, video_file_id):
    video = get_object_or_404(VideoFile, id=video_file_id)
    file_path = video.file.path

    if not os.path.isfile(file_path):
        return HttpResponseNotFound()
    response = RangedFileResponse(
        request, open(file_path, 'rb'),
        content_type=mimetypes.guess_type(file_path)[0]
    )
    response['Content-Length'] = os.path.getsize(file_path)
    return response