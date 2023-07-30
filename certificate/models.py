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

    def save(self, *args, **kwargs):
        if not self.pk:
            # Yeni bir sertifika oluşturulduğunda benzersiz bir kimlik atanır
            self.unique_id = get_random_string(length=10)
        return super().save(*args, **kwargs)




# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Course

# def course_detail(request, course_id):
#     course = get_object_or_404(Course, pk=course_id)

#     if request.method == 'POST':
#         certificate_file = request.FILES.get('certificate_file')

#         if certificate_file:
#             course.certificate = certificate_file
#             course.save()

#             # İşlem tamamlandıktan sonra başka sayfaya yönlendir
#             return redirect('course_detail', course_id=course_id)

#     context = {'course': course}
#     return render(request, 'course_detail.html', context)