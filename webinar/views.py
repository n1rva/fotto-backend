
from django.utils import timezone
from datetime import date

from account.serializers import UserSerializer
from account.models import UserProfile

from .serializers import SimplifiedWebinarSerializer, WebinarSerializer, WebinarTagSerializer
from .models import User, Webinar, WebinarTag

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated

from django.db.models import Prefetch

import ast


# Create your views here.




@api_view(['POST'])
@permission_classes([IsAdminUser]) 
def create_webinar(request):
    data = request.data
    data['participants'] = request.user.id

    tag_names = request.data.getlist('tags[]')
    
    tags = []
    for name in tag_names:
        capitalized_name = name.capitalize()
        tag, created = WebinarTag.objects.get_or_create(name=capitalized_name)
        tags.append(tag)

    serializer = WebinarSerializer(data=data)
    if serializer.is_valid():
        webinar = serializer.save()

        webinar.tags.set(tags)

        return Response({'success':True,'message': 'Webinar başarıyla oluşturuldu.', 'data':serializer.data}, status=status.HTTP_201_CREATED)  
    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def delete_webinar(request,webinar_id):
    try:
        webinar = Webinar.objects.get(id=webinar_id)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    
    webinar.delete()

    return Response({'success':True,'message': 'Webinar başarıyla silindi.'},status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAdminUser]) 
def update_webinar(request, webinar_id):

    data=request.data
    try:
        webinar = Webinar.objects.get(id=webinar_id)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    
    tag_names = request.data.getlist('tags[]')

    tags = []

    for name in tag_names:
        capitalized_name = name.capitalize()
        tag, created = WebinarTag.objects.get_or_create(name=capitalized_name)
        tags.append(tag)

    serializer = WebinarSerializer(webinar, data=data, partial=True)  

    if serializer.is_valid():
        serializer.save()

        webinar.tags.set(tags)

        return Response({'success':True,'message': 'Webinar başarıyla güncellendi.', 'webinar':serializer.data},status=status.HTTP_200_OK)

    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_webinar(request, webinar_id):
    try:
        webinar = Webinar.objects.get(id=webinar_id)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = WebinarSerializer(webinar, many=False)

    return Response({'success':True,'webinar': serializer.data})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def search_webinar(req, search_query):
    webinars = Webinar.objects.filter(title__icontains=search_query)

    serializer = WebinarSerializer(webinars, many=True)
    
    return Response({'success':True,'webinars': serializer.data})

@api_view(['GET'])
def get_webinar_by_slug(request, webinar_slug):
    try:
        webinar = Webinar.objects.get(slug=webinar_slug)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = WebinarSerializer(webinar, many=False)

    return Response({'success':True,'webinar': serializer.data})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_webinars(request):

  user_id = request.query_params.get('id')
  
  webinars = Webinar.objects.filter(participants=user_id)

  serializer = WebinarSerializer(webinars, many=True)

  return Response({'success':True,'webinars': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_active_webinars(req):

    current_datetime = timezone.now()

    active_webinars = Webinar.objects.filter(participants=req.user, date__gte=current_datetime) 

    active_serializer = SimplifiedWebinarSerializer(active_webinars, many=True)

    return Response({'success': True, 'webinars':active_serializer.data}) 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_expired_webinars(req):

    current_datetime = timezone.now()

    expired_webinars = Webinar.objects.filter(participants=req.user, date__lt=current_datetime)

    expired_serializer = SimplifiedWebinarSerializer(expired_webinars, many=True)

    return Response({'success': True, 'webinars':expired_serializer.data}) 

@api_view(['GET'])
def get_all_webinars(req):
    today= date.today()

    webinars= Webinar.objects.filter(date__gte=today)

    serializer = WebinarSerializer(webinars, many=True)

    return Response({
        'success':True, 'webinars':serializer.data
    })

@api_view(['GET'])
def get_expired_webinars(req):
    today= date.today()

    expiredWebinars= Webinar.objects.filter(date__lt=today).values()

    return Response({'success':True,'expiredWebinars': list(expiredWebinars)})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_webinar_participants(req,webinar_id):
    try:
        webinar = Webinar.objects.get(id=webinar_id)
        participants = webinar.participants.all()
        serializer = UserSerializer(participants, many=True)
        return Response({'success':True, 'participants':serializer.data})
    
    except Webinar.DoesNotExist:
        return Response({'success':False,'message': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_all_webinar_filters(req):
    tags = WebinarTag.objects.all()
    serializer = WebinarTagSerializer(tags, many=True)
    return Response({'success':True,'tags': serializer.data})

@api_view(['GET'])
def search_filters(req, search_query):
    tags = WebinarTag.objects.filter(name__icontains=search_query)
    serializer = WebinarTagSerializer(tags, many=True)
    return Response({'success':True,'tags': serializer.data})

@api_view(['GET'])
def webinars_by_tag(request,tag_names):

    tag_names = tag_names.split(',')

    tags = WebinarTag.objects.filter(name__in=tag_names)

    today= date.today()

    webinars = Webinar.objects.filter(tags__in=tags, date__gte=today)

    webinars = webinars.distinct()

    serializer = WebinarSerializer(webinars, many=True)

    return Response({'success':True, 'filtered_webinars':serializer.data})

    

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_webinar_from_user(req, webinar_id):
    args= {'id': webinar_id ,'participants' : req.data['user_id'] }

    try:
        webinar = Webinar.objects.get(**args)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bu kullanıcı için zaten silinmiş'}, status=status.HTTP_404_NOT_FOUND)

    webinar.participants.remove(req.user)
    return Response({'success':True,'message': 'Webinar kullanıcıdan başarıyla silindi.'},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_if_user_has_webinar(req, webinar_id):
    try:

        user = req.user

        webinar = Webinar.objects.get(id=webinar_id)

        if user in webinar.participants.all():
            return Response({'success':True,'has_webinar': True}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True,'has_webinar': False}, status=status.HTTP_200_OK)

    except Webinar.DoesNotExist:
        return Response({'error': 'Belirtilen webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)