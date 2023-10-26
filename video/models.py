from django.db import models
from django.contrib.auth.models import User

from django.utils.text import slugify

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.JSONField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    thumbnail = models.ImageField(upload_to='videos/thumbnail/',null=True, blank=True)
    date = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    instructor_image = models.ImageField(upload_to='videos/instructor/', null=True, blank=True)
    participants = models.ManyToManyField(User, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Video, self).save(*args, **kwargs)

class VideoFile(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE)
    file = models.FileField(upload_to='videos/records/')