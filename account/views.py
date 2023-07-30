from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets

from django.contrib.auth.hashers import make_password

from .validators import validate_password

from .serializers import SignUpSerializer, UserSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.contrib.auth.models import User

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

##SİL
@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def getAllUsers(request):
    users = User.objects.all().order_by('first_name')

    serializer = UserSerializer(users, many=True)

    return Response({'success':True, 'users':serializer.data})
##SİL

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



# @api_view(['GET'])
# @permission_classes([IsAdminUser]) 
# def search_users(request):
#     query = request.GET.get('query')

#     if query:
#         users = User.objects.filter(user__first_name__icontains=query) | User.objects.filter(user__last_name__icontains=query)
#     else:
#         users = User.objects.all()

#     return render(request, 'search_users.html', {'users': users})

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