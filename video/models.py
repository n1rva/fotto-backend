import re
from django.db import models
from django.contrib.auth.models import User

from django.utils.text import slugify

# Create your models here.

def custom_slugify(s):
    replacements = {
        'ç': 'c',
        'ğ': 'g',
        'ı': 'i',
        'ö': 'o',
        'ş': 's',
        'ü': 'u',
    }
    
    s = s.lower()
    
    for find, replace in replacements.items():
        s = s.replace(find, replace)
    
    s = re.sub(r'[^\w\s]', '', s)
    
    return slugify(s)

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.JSONField()
    tags = models.ManyToManyField('VideoTags', related_name='videos')
    source_certificate = models.FileField(upload_to='videos/source_certificates/',null= True, blank= True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    thumbnail = models.ImageField(upload_to='videos/thumbnail/',null=True, blank=True)
    date = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    instructor_image = models.ImageField(upload_to='videos/instructor/', null=True, blank=True)
    certificates_added = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.title)
        super(Video, self).save(*args, **kwargs)
    
            
    class Meta:
        ordering= ['-id']

class VideoTags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class VideoFile(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE)
    file = models.FileField(upload_to='videos/records/')

