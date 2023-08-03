import os
import re
from django.http import FileResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError, StreamingHttpResponse
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

        return Response({'success':True, 'video':serializer.data},status=status.HTTP_200_OK)     

   
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
   
   serializer = VideoSerializer(videos, many=True) 
   
   return Response({'success':True,'videos':serializer.data},status=status.HTTP_200_OK)


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

    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'Dosya yüklenemedi.'}, status=status.HTTP_400_BAD_REQUEST)

    video_file = VideoFile(video=video, file=file)
    video_file.save()

    serializer = VideoFileSerializer(video_file, many=False)
    return Response({'success': True, 'message': 'Webinar kaydı başarıyla yüklendi.', 'video_file': serializer.data})


# @api_view(['GET'])
# def stream_video_file(request, video_file_id):
#     try:
#         video_file = VideoFile.objects.get(video_id=video_file_id)
#         file_path = video_file.file.path
#         content_type = guess_type(file_path)[0]
        
#         response = Response(content_type=content_type)
#         response['X-Accel-Redirect'] = file_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
#         return response
#     except VideoFile.DoesNotExist:
#         return Response({'error': 'Webinar kaydı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    

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

# @api_view(['GET'])
# def stream_video(request, video_file_id):

#   try:
#     video = get_object_or_404(VideoFile, id=video_file_id)
#     range_header = request.META.get('HTTP_RANGE', '').strip()
#     range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

#     range_match = range_re.match(range_header)
#     first_byte, last_byte = 0, None

#     print(range_match)

#     if range_match:
#       first_byte = int(range_match.group(1))
#       last_byte = first_byte + 1024  


#       if range_match.group(2):
#          last_byte = int(range_match.group(2))

#       if last_byte >= os.path.getsize(video.file.path):  
#          last_byte = os.path.getsize(video.file.path) - 1

#     bytes_to_send = last_byte - first_byte + 1

#     resp = StreamingHttpResponse(chunked_video(video.file.path, first_byte, last_byte), status=206)
#     resp['Content-Type'] = 'video/mp4'
#     resp['Content-Length'] = str(bytes_to_send)
#     resp['Content-Range'] = 'bytes %s-%s/%s' %(first_byte, last_byte, os.path.getsize(video.file.path))
    
#     return resp

#   except:
#     return Response(status=status.HTTP_400_BAD_REQUEST)


# def chunked_video(path, start, end):
#   with open(path, 'rb') as f:
#     f.seek(start) 
#     while True:
#        data_chunk = f.read(1024)
#        if not data_chunk:
#          break
#        yield data_chunk

########################################################################

# @api_view(['GET'])
# def stream_video(request, video_file_id):

#   try:
#     video = get_object_or_404(VideoFile, id=video_file_id)


#     range_header = request.META.get('HTTP_RANGE', '').strip()
#     range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I) 
#     range_match = range_re.match(range_header)
    
#     first_byte = int(range_match.group(1))
#     last_byte = first_byte + 4096

#     if range_match.group(2):
#         last_byte = int(range_match.group(2))

#     chunk_size = 4096
#     total_size = os.path.getsize(video.file.path)

#     if last_byte >= total_size:
#         last_byte = total_size - 1

#     bytes_to_send = last_byte - first_byte + 1

#     stream = get_video_stream(video, chunk_size, first_byte, last_byte)
#     mime_type = get_video_mime_type(video.name) 

#     response = StreamingHttpResponse(stream, status=206, content_type=mime_type)

#     content_length = bytes_to_send
#     content_range = 'bytes %s-%s/%s' % (first_byte, last_byte, total_size)

#     response['Content-Length'] = str(content_length) 
#     response['Content-Range'] = content_range
#     return response

#   except FileNotFoundError:
#     return HttpResponseNotFound()
#   except IsADirectoryError:
#     return HttpResponseBadRequest()
#   except:
#     return HttpResponseServerError()


# def get_video_stream(video, chunk_size, start, end):
#   with open(video.path, 'rb') as f:
#     f.seek(start)
#     while True:
#        data = f.read(chunk_size)
#        if not data:
#          break
#        yield data

# def get_video_mime_type(name):
#   # video uzantısına göre mime type döndür
#   if name.endswith('.mp4'):
#     return 'video/mp4'

 ########################################################


@api_view(['GET'])
def stream_video(request, video_file_id):
    try:
        video = get_object_or_404(VideoFile, id=video_file_id)
        file_path = video.file.path
        print(file_path)
        content_type = 'video/mp4' 

        response = StreamingHttpResponse(file_iterator(file_path), content_type=content_type)
        response['Content-Length'] = os.path.getsize(file_path)
        # response['Access-Control-Allow-Origin'] = 'http://localhost:3000'

        return response

    except VideoFile.DoesNotExist:
        return HttpResponseNotFound()

def file_iterator(file_path, chunk_size=8192):
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            yield data
