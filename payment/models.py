from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Payment(models.Model):

    PRODUCT_TYPES = (
            ('video', 'Video'),
            ('webinar', 'Webinar'),
    )

    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)
    product_id = models.IntegerField()
    order_unique_id = models.CharField(max_length=16, unique=True)
    address = models.CharField(max_length=200)
    phone_number = models.CharField()
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, unique=False)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=16, decimal_places=2)
    status = models.IntegerField()

class PaymentNotification(models.Model):
        
        PRODUCT_TYPES = (
                ('video', 'Video'),
                ('webinar', 'Webinar'),
        )

        product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)
        is_read = models.BooleanField(default=False)
        title= models.CharField(max_length=200)
        price= models.DecimalField(max_digits=16, decimal_places=2)
        date = models.DateTimeField()
        user = models.ForeignKey(User,
                on_delete=models.CASCADE, unique=False)
        
        class Meta:
                ordering= ['-id']