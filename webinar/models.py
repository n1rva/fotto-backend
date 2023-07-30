from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Webinar(models.Model):
    title = models.CharField(max_length=200)
    description = models.JSONField()
    source_certificate = models.FileField(upload_to='webinars/source_certificates/',null= True, blank= True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='webinars/main/', null=True, blank=True)
    date = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    instructor_image = models.ImageField(upload_to='webinars/instructor/', null=True, blank=True)
    participants = models.ManyToManyField(User, blank=True)
    certificates_added = models.BooleanField(default=False)