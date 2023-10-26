from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets

from django.contrib.auth.hashers import make_password

from .validators import validate_password

from .serializers import ChangePasswordSerializer, SignUpSerializer, UserSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.contrib.auth.models import User

from django.contrib.auth import update_session_auth_hash

from django.core.mail import send_mail
from django.template.loader import render_to_string

# Create your views here.


@api_view(['POST'])
def signup(request):
    data = request.data

    user = SignUpSerializer(data=data)

    if user.is_valid():
        if not User.objects.filter(email=data['email']).exists():
            user = User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                username=data['email'],
                email=data['email'],
                password=make_password(data['password'])
            )

            subject = "Fizyotto Live'e hoşgeldiniz!"
            from_email = 'destek@fizyottolive.com'
            recipient_list = [data['email']]

            email_template = 'email/welcome_email.html'
            text_content= 'email/welcome_email.txt'

            email_content_txt = render_to_string(text_content)
            email_content_html = render_to_string(email_template)

            send_mail(subject, email_content_txt, from_email, recipient_list, html_message=email_content_html)

            return Response({
                'success':True,
                'message': 'Kayıt başarılı.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response({
                'success':False,
                'message': 'Kullanıcı zaten var'},
                status=status.HTTP_400_BAD_REQUEST
            )

    else:
        return Response({'success':True,'message':user.errors})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request):

    user = UserSerializer(request.user)

    res = user.data
    res['is_admin'] = request.user.is_staff

    return Response(res)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):

    user = get_object_or_404(User, id=pk)

    serializer = UserSerializer(user, many=False)

    return Response({'success':True, 'user':serializer.data})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)

    if 'email' in request.data:
        user.email = request.data['email']

    serializer.save()

    return Response({'success': True, 'user': serializer.data}, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_password(request):
    user = request.user

    if 'currentPassword' in request.data and 'newPassword' in request.data and 'confirmNewPassword' in request.data:
        current_password = request.data['currentPassword']
        new_password = request.data['newPassword']
        confirm_new_password = request.data['confirmNewPassword']

        # Validate current password
        if not user.check_password(current_password):
            return Response({'success': False, 'message': 'Geçerli şifrenizi yanlış girdiniz.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate new password
            validate_password(new_password)

            # Check if new password and confirm new password match
            if new_password != confirm_new_password:
                return Response({'success': False, 'message': 'Yeni şifreler eşleşmiyor.'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password and save the user
            user.set_password(new_password)
            user.save()

            return Response({'success': True, 'message': 'Şifre başarıyla güncellendi.'}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'success': False, 'message': str(e)[2:-2]}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'success': False, 'message': 'Yeni şifre ya da geçerli şifre sağlanmadı.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])  
def userSearch(request):
    query = request.query_params.get('q')
    
    if query:
        first_name_results = User.objects.filter(first_name__icontains=query)
        last_name_results = User.objects.filter(last_name__icontains=query)    
        users = (first_name_results | last_name_results).distinct()[:5]
    else:
        users = User.objects.all()
        
    serializer = UserSerializer(users, many=True)  
    return Response({'success':True, 'message':'Kullanıcılar bulundu.', 'users':serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)