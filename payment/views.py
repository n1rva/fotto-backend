from multiprocessing import process
import os
from time import timezone
from urllib import request
from django.http import HttpResponse
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import base64
import hmac
import hashlib
import requests
import json
import uuid

from datetime import datetime

from account.serializers import UserSerializer
from django.contrib.auth.models import User

from .paginations import CustomPagination

from .models import Payment, PaymentNotification
from webinar.models import Webinar
from video.models import Video

from .serializers import PaymentNotificationSerializer, PaymentSerializer

from django.core.mail import send_mail
from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated,IsAdminUser

@api_view(['POST'])
def payment_first_step(req):

    data = req.data
    user = req.user

    order_unique_id= str(uuid.uuid4().hex)[:16]
    date= datetime.now()
    status= 2

    order_data = {
        'product_type': data['product_type'],
        'product_id': data['product_id'],
        'order_unique_id': order_unique_id,
        'address': data['address'],
        'phone_number': data['phone_number'],
        'user': user.id,
        'date': date,
        'price': data['price'],
        'status': status
    }

    merchant_id= os.environ.get('MERCHANT_ID')

    merchant_key=  bytes(os.environ.get('MERCHANT_KEY'), 'utf-8')

    merchant_salt= bytes(os.environ.get('MERCHANT_SALT'), 'utf-8')

    user_ip= data['ip']
    merchant_oid = order_unique_id 
    payment_amount = data['price']
    user_basket = base64.b64encode(json.dumps([data['userBasket']]).encode())
    
    debug_on= '1'
    currency='TL'
    no_installment = '1'
    max_installment = '0'

    email= user.email
    name=user.first_name + user.last_name

    hash_str = merchant_id + user_ip + merchant_oid + email + payment_amount + user_basket.decode() + no_installment + max_installment + currency 

    paytr_token = base64.b64encode(hmac.new(merchant_key, hash_str.encode() + merchant_salt, hashlib.sha256).digest())

    params = {
        'merchant_id': merchant_id,
        'user_ip': user_ip,
        'merchant_oid': merchant_oid,
        'email': email,
        'payment_amount': payment_amount,
        'paytr_token': paytr_token,
        'user_basket': user_basket,
        'debug_on': debug_on,
        'no_installment': no_installment,
        'max_installment': max_installment,
        'user_name': name,
        'user_address': data['address'],
        'user_phone': data['phone_number'],
        'merchant_ok_url': 'https://fizyottolive.com/payment/success',
        'merchant_fail_url': 'https://fizyottolive.com/payment/failure',
        'timeout_limit': '30' ,
        'currency': currency,
    }

    result = requests.post('https://www.paytr.com/odeme/api/get-token', params)
    res = json.loads(result.text)

    if res['status'] == 'success':

        serializer = PaymentSerializer(data=order_data)
        if serializer.is_valid():
            serializer.save()

            return Response({'success':True,'message': 'Ödeme yapılıyor...', 'token':res['token']} )  

        else:
            return Response({'success':False,'message': 'Ödeme Yapılamadı'})
    else:
        return Response({'success':False,'message': 'Ödeme Yapılamadı'})
    
@api_view(['POST'])
def payment_last_step(request):

    post = request.POST

    merchant_key=  bytes(os.environ.get('MERCHANT_KEY'), 'utf-8')

    merchant_salt= os.environ.get('MERCHANT_SALT')

    # Bu kısımda herhangi bir değişiklik yapmanıza gerek yoktur.
    # POST değerleri ile hash oluştur.
    hash_str = post['merchant_oid'] + merchant_salt + post['status'] + post['total_amount']
    hash = base64.b64encode(hmac.new(merchant_key, hash_str.encode(), hashlib.sha256).digest())

    # Oluşturulan hash'i, paytr'dan gelen post içindeki hash ile karşılaştır
    # (isteğin paytr'dan geldiğine ve değişmediğine emin olmak için)
    # Bu işlemi yapmazsanız maddi zarara uğramanız olasıdır.
    if hash != bytes(post['hash'], 'utf-8'):
        return HttpResponse(str('PAYTR notification failed: bad hash'))

    # BURADA YAPILMASI GEREKENLER
    # 1) Siparişin durumunu post['merchant_oid'] değerini kullanarak veri tabanınızdan sorgulayın.
    # 2) Eğer sipariş zaten daha önceden onaylandıysa veya iptal edildiyse "OK" yaparak sonlandırın.

    order_unique_id= post['merchant_oid']

    order = Payment.objects.get(order_unique_id=order_unique_id)

    if order.status != 2:
        return HttpResponse(str('OK'))


    if post['status'] == 'success':  # Ödeme Onaylandı
        """
        BURADA YAPILMASI GEREKENLER
        1) Siparişi onaylayın.
        2) Eğer müşterinize mesaj / SMS / e-posta gibi bilgilendirme yapacaksanız bu aşamada yapmalısınız.
        3) 1. ADIM'da gönderilen payment_amount sipariş tutarı taksitli alışveriş yapılması durumunda değişebilir. 
        Güncel tutarı post['total_amount'] değerinden alarak muhasebe işlemlerinizde kullanabilirsiniz.
        """
        if order.product_type=='webinar':
            webinar = Webinar.objects.get(id=order.product_id)
            user=order.user

            webinar.participants.add(user.id)
            order.status=1
            order.save()

            now=datetime.now()

            notification_data={
                'product_type':'webinar',
                'title':webinar.title,
                'price':webinar.price,
                'date':now,
                'user':user
            }

            PaymentNotification.objects.create(**notification_data)


            subject = "Ödemeniz onaylandı!"
            from_email = 'destek@fizyottolive.com'
            recipient_list = [post['email']]

            email_template = 'email/payment_successful.html'
            text_content= 'email/payment_successful.txt'

            email_content_txt = render_to_string(text_content)
            email_content_html = render_to_string(email_template)

            send_mail(subject, email_content_txt, from_email, recipient_list, html_message=email_content_html)


            return Response(str('OK'))      
          
        if order.product_type=='video':
            video = Video.objects.get(id=order.product_id)
            user=order.user

            video.participants.add(user.id)
            order.status=1
            order.save()

            now=datetime.now()

            notification_data={
                'product_type':'video',
                'title':video.title,
                'price':video.price,
                'date':now,
                'user':user
            }

            PaymentNotification.objects.create(**notification_data)

            subject = "Ödemeniz onaylandı!"
            from_email = 'destek@fizyottolive.com'
            recipient_list = [post['email']]

            email_template = 'email/payment_successful.html'
            text_content= 'email/payment_successful.txt'

            email_content_txt = render_to_string(text_content)
            email_content_html = render_to_string(email_template)

            send_mail(subject, email_content_txt, from_email, recipient_list, html_message=email_content_html)



            return Response(str('OK'))
        
    else:  # Ödemeye Onay Verilmedi
        """
        BURADA YAPILMASI GEREKENLER
        1) Siparişi iptal edin.
        2) Eğer ödemenin onaylanmama sebebini kayıt edecekseniz aşağıdaki değerleri kullanabilirsiniz.
        post['failed_reason_code'] - başarısız hata kodu
        post['failed_reason_msg'] - başarısız hata mesajı
        """

        if order.product_type=='webinar':
            webinar = Webinar.objects.get(id=order.product_id)

            order.status=0
            order.save()

            return Response(str('Fail'))      
          
        if order.product_type=='video':
            webinar = Webinar.objects.get(id=order.product_id)

            order.status=0
            order.save()


            return Response(str('Fail'))

    # Bildirimin alındığını PayTR sistemine bildir.
    return HttpResponse(str('OK'))

@api_view(['PUT'])
@permission_classes([IsAdminUser]) 
def update_notification(request, notification_id):

    data=request.data
    
    notification= PaymentNotification.objects.get(id=notification_id)

    serializer= PaymentNotificationSerializer(notification,data=data, partial=True)

    if serializer.is_valid():
        serializer.save()

        return Response({'success':True, 'msg':'Bildirim güncellendi.'})
    
    return Response({'success':False, 'msg':'Bildirim güncellenirken hata ile karşılaşıldı.'})

@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def get_unread_notifications(request,type):

    notifications= PaymentNotification.objects.filter(is_read=False, product_type=type)

    paginator= CustomPagination()
    results_page = paginator.paginate_queryset(notifications, request)

    serializer= PaymentNotificationSerializer(results_page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def get_read_notifications(request, type):

    notifications= PaymentNotification.objects.filter(is_read=True, product_type=type)

    paginator= CustomPagination()

    results_page = paginator.paginate_queryset(notifications, request)

    serializer= PaymentNotificationSerializer(results_page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def deneme(request):

    user_instance = User.objects.get(id=request.user.id)

    now=datetime.now()
    notification_data={
        'product_type':'video',
        'title':'Omurga İlişikili Temporomandibular Eklem (TME) Disfonksiyonlarında Rehabilitasyon Prensibleri',
        'price':200,
        'date':now,
        'user':user_instance
    }

    data= PaymentNotification.objects.create(**notification_data)

    # notification_serializer = PaymentNotificationSerializer(data=notification_data)

    if data:
        return Response({'success':True})

    return Response({'success':False})