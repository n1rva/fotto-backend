from enum import unique
import os
from urllib import request
from cairo import FontWeight
from django.shortcuts import render

from pathlib import Path

from webinar.serializers import WebinarSerializer

from .serializers import CertificateSerializer
from .models import Certificate, User, Webinar
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .validators import validate_file_extension

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.conf import settings
from django.utils.crypto import get_random_string

import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

from django.http import FileResponse, HttpResponse
import io

from django.core.files.base import ContentFile

import uuid

from reportlab_qr_code import qr_draw

# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent

def createCertficate(name, font_size, color, y_axis, max_text_width, max_font_size, font, source_pdf, unique_id, id_x_axis, id_y_axis, id_font_size, id_font, id_color, qr_x, qr_y, qr_size, qr_bg, qr_fg ):
    if source_pdf == '':
        return Response({ 'error': 'Lütfen kaynak pdfi yükleyin' }, status=status.HTTP_400_BAD_REQUEST)
    
    isValidFile = validate_file_extension(source_pdf.name)

    if not isValidFile:
        return Response({ 'error': 'PDF kaynak dosyası pdf uzantılı değil.' }, status=status.HTTP_400_BAD_REQUEST)

    existingPdf= PdfReader(source_pdf)
    page= existingPdf.pages[0]

    packet= io.BytesIO()

    page_size= [float(page.mediabox.width) ,float(page.mediabox.height)]

    pdf = canvas.Canvas(packet, pagesize=(page_size[0], page_size[1]))

    if isinstance(font, str):
        fontName = font.split('.')[0]
    else:
        fontName = font.name

    unique_id_font_name = id_font.split('.')[0]


    reportlab.rl_config.TTFSearchPath.append(os.path.join(BASE_DIR, 'static') + '/fonts')

    pdfmetrics.registerFont(TTFont(fontName, font))
    pdfmetrics.registerFont(TTFont(unique_id_font_name,id_font ))

    while(True):
        textWidth = pdf.stringWidth(name, fontName, font_size)

        if(textWidth >max_text_width * inch):
            break
        
        font_size +=1

        if(font_size==max_font_size):
            break

    
    #user name
    pdf.setFont(fontName, font_size)
    pdf.setFillColor(HexColor(color))
    pdf.drawCentredString(page_size[0]/2, y_axis * inch, name, )

    #unique_id
    parstyle = ParagraphStyle(name=unique_id , fontName=unique_id_font_name, fontSize=id_font_size, textColor=id_color)
    
    p = Paragraph(f"Sertifika No: <b>{unique_id}</b>", parstyle)
    p.wrapOn(pdf, 10*inch, 1*inch)
    p.drawOn(pdf, (id_x_axis+1)*inch, id_y_axis*inch)


    qr_draw(pdf, f'https://localhost:3000/certificates/{unique_id}', x=qr_x* inch, y=qr_y *inch , size=qr_size*inch, bg=qr_bg, fg=qr_fg )
    
    pdf.save()

    packet.seek(0)

    newPdf= PdfReader(packet)

    output= PdfWriter()

    page.merge_page((newPdf.pages[0]))
    output.add_page(page)

    # packet.truncate(0)

    output.write(packet)

    return ContentFile(packet.getvalue())

def create_unique_id():

    unique_id = str(uuid.uuid4())[:10]  

    while Certificate.objects.filter(unique_id=unique_id).exists():
        unique_id = str(uuid.uuid4())[:10]

    return unique_id


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser]) 
def single_certificate_views(request):

    if request.method == 'GET':
        return get_user_certificate_info(request)
    if request.method == 'POST':
        return create_certificate_for_user(request)
    
@api_view(['DELETE', 'POST'])
@permission_classes([IsAdminUser]) 
def handle_certificate_by_id(request):

    if request.method == 'DELETE':
        return deleteCertificate(request)
    if request.method == 'POST':
        return updateCertificate(request)
    


@api_view(['POST']) #pdf olarak bir pencere içine gönderilebilir
@permission_classes([IsAdminUser]) 
def preview_certificate(request):

    data = request.data

    name= data['name']
    font_size= int(data['font_size'])
    color = data['color']
    max_text_width= float(data['max_text_width'])
    max_font_size= int(data['max_font_size']) 
    webinar_id = int(data['webinar_id'])
    y_axis = float(data['y_axis'])

    id_x_axis = float(data['id_x_axis'])
    id_y_axis = float(data['id_y_axis'])
    id_font_size = int(data['id_font_size'])
    id_font = data['id_font']
    id_color = data['id_color']    
    
    qr_x = float(data['qr_x'])
    qr_y = float(data['qr_y'])
    qr_size = float(data['qr_size'])
    qr_bg = data['qr_bg']
    qr_fg = data['qr_fg']

    if 'fontFile' in request.FILES:
        font = request.FILES['fontFile']
    else:
        font= data['font']

    sourceWebinar = Webinar.objects.get(id=webinar_id) #sadece certificate için filter
    sourcePDF= sourceWebinar.source_certificate

    unique_id=create_unique_id()

    packet= createCertficate(name, font_size, color, y_axis, max_text_width, max_font_size, font, sourcePDF, unique_id, id_x_axis, id_y_axis, id_font_size, id_font, id_color, qr_x, qr_y, qr_size, qr_bg, qr_fg)

    response = HttpResponse(packet, content_type='application/pdf') # ---> Reponse??
    response['Content-Disposition'] = f'attachment; filename="{get_random_string(length=6)}.pdf"'

    return response

@api_view(['POST'])
@permission_classes([IsAdminUser]) 
def create_certificate_for_participants(request):
    data = request.data

    webinar_id = data['webinar_id']
    webinar = Webinar.objects.get(id=webinar_id)

    sourcePDF= webinar.source_certificate

    for participant in webinar.participants.all():

        name = f"{participant.first_name} {participant.last_name}" 

        font_size= int(data['font_size'])
        color = data['color']
        max_text_width= float(data['max_text_width'])
        max_font_size= int(data['max_font_size']) 
        webinar_id = int(data['webinar_id'])
        y_axis = float(data['y_axis'])

        id_x_axis = float(data['id_x_axis'])
        id_y_axis = float(data['id_y_axis'])
        id_font_size = int(data['id_font_size'])
        id_font = data['id_font']
        id_color = data['id_color']    
        
        qr_x = float(data['qr_x'])
        qr_y = float(data['qr_y'])
        qr_size = float(data['qr_size'])
        qr_bg = data['qr_bg']
        qr_fg = data['qr_fg']

        if 'fontFile' in request.FILES:
            font = request.FILES['fontFile']
        else:
            font= data['font']

        unique_id=create_unique_id()

        certificateFile = createCertficate(name, font_size, color, y_axis, max_text_width, max_font_size, font, sourcePDF, unique_id, id_x_axis, id_y_axis, id_font_size, id_font, id_color, qr_x, qr_y, qr_size, qr_bg, qr_fg)

        
        certificate = Certificate.objects.create(user=participant, webinar=webinar )
        certificate.certificate_file.save(f'{webinar_id}__{participant.first_name}_{participant.last_name}.pdf', ContentFile(certificateFile.read()))
        certificate.save()


    return Response({'success':True, 'message':'Sertifikalar katılımcılar için başarıyla oluşturuldu.'})


def create_certificate_for_user(request):

    data = request.data

    userID = int(data['userID'])
    font_size= int(data['font_size'])
    color = data['color']
    max_text_width= float(data['max_text_width'])
    max_font_size= int(data['max_font_size']) 
    webinar_id = int(data['webinar_id'])
    y_axis = float(data['y_axis'])

    id_x_axis = float(data['id_x_axis'])
    id_y_axis = float(data['id_y_axis'])
    id_font_size = int(data['id_font_size'])
    id_font = data['id_font']
    id_color = data['id_color']    
    
    qr_x = float(data['qr_x'])
    qr_y = float(data['qr_y'])
    qr_size = float(data['qr_size'])
    qr_bg = data['qr_bg']
    qr_fg = data['qr_fg']

    if 'fontFile' in request.FILES:
        font = request.FILES['fontFile']
    else:
        font= data['font']

    sourceWebinar = Webinar.objects.get(id=webinar_id)
    sourcePDF= sourceWebinar.source_certificate

    user = User.objects.get(id=userID)

    name=user.first_name + " " + user.last_name

    unique_id=create_unique_id()

    certificateFile= createCertficate(name, font_size, color, y_axis, max_text_width, max_font_size, font, sourcePDF, unique_id, id_x_axis, id_y_axis, id_font_size, id_font, id_color, qr_x, qr_y, qr_size, qr_bg, qr_fg)

    certificate = Certificate.objects.create(user=user, webinar=sourceWebinar )

    certificate.certificate_file.save(f'{webinar_id}__{user.first_name}_{user.last_name}.pdf', ContentFile(certificateFile.read()))
    certificate.save()

    
    # for user in User.objects.all():
    #     name=user.first_name + " " + user.last_name
        
    #     certificateFile = createCertficate(name, fontSize, color, maxTextWidth, maxFontSize, fontFile, sourcePDF)

    #     Certificate.objects.create(user=user, webinar=Webinar.objects.filter(id=7)[0], certificate_file=certificateFile )

    # pocket= createCertficate(name, fontSize, color, maxTextWidth, maxFontSize, fontFile, sourcePDF)

    # response = HttpResponse(pocket.getvalue(), content_type='application/pdf') # ---> Reponse??
    # response['Content-Disposition'] = f'attachment; filename="{get_random_string(length=6)}.pdf"'

    return Response({'success':True, 'message':'Sertifika başarıyla oluşturuldu.'})


def deleteCertificate(request,id):
    certificate = get_object_or_404(Certificate, id=id)
    
    certificate.delete()

    return Response({'success':True ,'message': 'Sertifika başarıyla silindi.'},status=status.HTTP_200_OK)


def updateCertificate(request, pk):
    certificate = get_object_or_404(Certificate, id=pk)

    certificate.certificate_file = request.data['certificate_file']

    certificate.save()

    serializer = CertificateSerializer(certificate, many=False)

    return Response({'message': 'Sertifika dosyası başarıyla düzeltildi.', 'data':serializer.data})

@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def getCertificate(request, pk):
    certificate = get_object_or_404(Certificate, id=pk)

    serializer = Certificate(certificate, many=False)

    return Response({'certificate': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_certificates(request):
    user_id = request.user.id

    certificates = Certificate.objects.filter(user_id=user_id)

    filtered_certificates = certificates.exclude(webinar__certificates_added=False)

    serializer = CertificateSerializer(filtered_certificates, many=True)
    return Response({'success': True, 'certificates': serializer.data})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_current_user_certificates(request):

#     args = { 'user': request.user.id }

#     certificates = Certificate.objects.filter(**args)

#     serializer = CertificateSerializer(certificates, many=True)

#     return Response({'success':True,'certificates': serializer.data})


def get_user_certificate_info(request):

    user_id = request.query_params.get('userid')
    
    certificates = Certificate.objects.filter(user=user_id)
    
    serializer = CertificateSerializer(certificates, many=True)

    return Response({'success':True, 'certificates': serializer.data})

@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def getWebinarCertificates(request):

    args = { 'webinar': request.webinar.id }

    certificates = Certificate.objects.filter(**args)

    serializer = Certificate(certificates, many=True)

    return Response({'certificates': serializer.data})


@api_view(['POST'])
def get_certificate_by_unique_id(request):

    data = request.data
    unique_id = data.get('unique_id')

    certificate = Certificate.objects.get(unique_id=unique_id)

    try:
        file = open(settings.MEDIA_ROOT + '/' + certificate.certificate_file.name, 'rb')
        file_content = file.read()
        return HttpResponse(file_content, content_type='application/pdf')
    except IOError:
        return Response({'success': False, 'message': 'Dosya bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    finally:
        file.close()




@api_view(['GET'])
def verify_certificate(request):
    unique_id = request.query_params.get('q')

    try:
        certificate = Certificate.objects.get(unique_id=unique_id)
        serializer = CertificateSerializer(certificate, many=False)

        webinar_serializer = WebinarSerializer(certificate.webinar)

        webinar_data=webinar_serializer.data

        data=serializer.data

        data['date']=webinar_data['date']
        data['title']=webinar_data['title']

    except Certificate.DoesNotExist:
        return Response({'success': False, "message": "Sertifika bulunamadı"})


    return Response({'success': True, "message": "Sertifika mevcut", 'data': data,})
