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
from .pagination import CustomPagination

from .serializers import VideoFileSerializer, VideoSerializer, VideoTagSerializer

from .models import Video, VideoFile, VideoTags

from django.utils.http import http_date

from django.core.exceptions import ObjectDoesNotExist

from ranged_response import RangedFileResponse

# Create your views here.

@api_view(['POST']) 
@permission_classes([IsAdminUser]) 
def create_video(request):
    data = request.data
    data['participants'] = request.user.id

    tag_names = request.data.getlist('tags[]')
    
    tags = []
    for name in tag_names:
        capitalized_name = name.capitalize()
        tag, created = VideoTags.objects.get_or_create(name=capitalized_name)
        tags.append(tag)

    serializer = VideoSerializer(data=data)

    if serializer.is_valid():
        video = serializer.save()

        video.tags.set(tags)

        return Response({'success':True,'message': 'Webinar kaydı başarıyla oluşturuldu.', 'video':serializer.data}, status=status.HTTP_201_CREATED)  

    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser]) 
def update_video(request, video_id):
    
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return Response({'error': 'Video bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

    tag_names = request.data.getlist('tags[]')
    
    tags = []
    for name in tag_names:
        capitalized_name = name.capitalize()
        tag, created = VideoTags.objects.get_or_create(name=capitalized_name)
        tags.append(tag)

    serializer = VideoSerializer(video, data=request.data, partial=True)  
   
    if serializer.is_valid():
        serializer.save()

        video.tags.set(tags)

        return Response({'success':True,'message': 'Webinar kaydı başarıyla güncellendi.', 'video':serializer.data},status=status.HTTP_200_OK)

    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def delete_video(request,video_id):
    try:
        video = Video.objects.get(id=video_id) # exception yakala
        
        video.delete()
        
        return Response({'success':True, 'message':'Webinar kaydı başarıyla silindi.'},status=status.HTTP_200_OK)     
    
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
def get_video_by_slug(request,video_slug):
   try:
        video = Video.objects.get(slug=video_slug)  
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
@permission_classes([IsAdminUser])
def search_video(req, search_query):
    videos = Video.objects.filter(title__icontains=search_query)

    serializer = VideoSerializer(videos, many=True)
    
    return Response({'success':True,'videos': serializer.data})


@api_view(['GET'])
def get_videos(req):
    all_videos = Video.objects.all().order_by('-id')

    paginator= CustomPagination()

    results_page = paginator.paginate_queryset(all_videos, req)

    serializer = VideoSerializer(results_page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_videos(request):

  user_id = request.query_params.get('user_id')

  if not user_id:
    return Response({"error": "User ID gerekli."}, status=400)
  
  try:
    videos = Video.objects.filter(participants=user_id)
    
    if not videos:
      return Response({'success':True,'videos': []}, status=status.HTTP_200_OK)

    serializer = VideoSerializer(videos, many=True)
    return Response({'success':True, 'videos':serializer.data}, status=status.HTTP_200_OK)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_if_user_has_video(req, video_id):
    try:
        user = req.user

        video = Video.objects.get(id=video_id)

        if user in video.participants.all():
            return Response({'success':True,'has_video': True}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True,'has_video': False}, status=status.HTTP_200_OK)

    except Video.DoesNotExist:
        return Response({'error': 'Belirtilen video bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_all_video_filters(req):
    tags = VideoTags.objects.all()
    serializer = VideoTagSerializer(tags, many=True)
    return Response({'tags': serializer.data})

@api_view(['GET'])
def search_filters(req, search_query):
    tags = VideoTags.objects.filter(name__icontains=search_query)
    serializer = VideoTagSerializer(tags, many=True)
    return Response({'tags': serializer.data})

@api_view(['GET'])
def videos_by_tags(request,tag_names):

    tag_names = tag_names.split(',')

    tags = VideoTags.objects.filter(name__in=tag_names)

    videos = Video.objects.filter(tags__in=tags)

    videos = videos.distinct()

    paginator= CustomPagination()
    results_page = paginator.paginate_queryset(videos, request)

    serializer = VideoSerializer(results_page, many=True)

    return paginator.get_paginated_response(serializer.data)

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
        return Response({'success':'False','error': 'Webinar kaydı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

    video_file.file.delete()
    video_file.delete()

    return Response({'success': True, 'message': 'Webinar kaydı başarıyla silindi.'})

range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request, video_slug):
    video= get_object_or_404(Video, slug=video_slug)
    video_file = get_object_or_404(VideoFile, video=video)
    path = video_file.file.path

    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp