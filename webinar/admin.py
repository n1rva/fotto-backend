from django.contrib import admin

from .models import Webinar, WebinarTag

# Register your models here.

admin.site.register(Webinar)
admin.site.register(WebinarTag)