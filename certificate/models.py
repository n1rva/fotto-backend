from django.db import models
from django.contrib.auth.models import User

from webinar.models import Webinar
from django.utils.crypto import get_random_string

# Create your models here.


class Certificate(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, unique=False)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, unique=False )
    unique_id = models.CharField(max_length=10, unique=True)
    certificate_file = models.FileField(upload_to='certificates/')

    class Meta:
        unique_together = ('user', 'webinar',)