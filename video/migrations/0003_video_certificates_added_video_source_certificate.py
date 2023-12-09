# Generated by Django 4.2 on 2023-11-07 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_video_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='certificates_added',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='video',
            name='source_certificate',
            field=models.FileField(blank=True, null=True, upload_to='videos/source_certificates/'),
        ),
    ]