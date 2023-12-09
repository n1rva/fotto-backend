from django.contrib import admin

from .models import Payment, PaymentNotification

# Register your models here.

admin.site.register(Payment)
admin.site.register(PaymentNotification)