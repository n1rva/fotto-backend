
from django.utils import timezone
from datetime import date

from account.serializers import UserSerializer
from account.models import UserProfile

from .serializers import WebinarSerializer
from .models import User, Webinar

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated

import ast


# Create your views here.




@api_view(['POST'])
@permission_classes([IsAdminUser]) 
def create_webinar(request):
    data = request.data
    data['participants'] = request.user.id

    serializer = WebinarSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
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
    try:
        webinar = Webinar.objects.get(id=webinar_id)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    
    
    serializer = WebinarSerializer(webinar, data=request.data, partial=True)  

    if serializer.is_valid():
        serializer.save()
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
def get_user_webinars(request):

  user_id = request.query_params.get('id')
  
  webinars = Webinar.objects.filter(participants=user_id)

  serializer = WebinarSerializer(webinars, many=True)

  return Response({'success':True,'webinars': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_webinars(req):

    current_datetime = timezone.now()

    active_webinars = Webinar.objects.filter(participants=req.user, date__gte=current_datetime) 
    expired_webinars = Webinar.objects.filter(participants=req.user, date__lt=current_datetime)

    active_serializer = WebinarSerializer(active_webinars, many=True)
    expired_serializer = WebinarSerializer(expired_webinars, many=True)

    data = {
    'active': active_serializer.data,
    'expired': expired_serializer.data,
    }

    return Response({'success': True, 'webinars':data}) 

@api_view(['GET'])
def get_all_webinars(req):

    webinars= Webinar.objects.all()

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
def get_webinar_participants(req,webinar_id):
    try:
        webinar = Webinar.objects.get(id=webinar_id)
        participants = webinar.participants.all()
        serializer = UserSerializer(participants, many=True)
        return Response({'success':True, 'participants':serializer.data})
    
    except Webinar.DoesNotExist:
        return Response({'success':False,'message': 'Webinar bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

    

@api_view(['DELETE'])
def delete_webinar_from_user(req, webinar_id):
    args= {'id': webinar_id ,'participants' : req.data['user_id'] }

    try:
        webinar = Webinar.objects.get(**args)
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar bu kullanıcı için zaten silinmiş'}, status=status.HTTP_404_NOT_FOUND)

    webinar.participants.remove(req.user)
    return Response({'success':True,'message': 'Webinar kullanıcıdan başarıyla silindi.'},status=status.HTTP_200_OK)