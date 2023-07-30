# Generated by Django 4.2 on 2023-07-13 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_alter_video_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='instructor_image',
            field=models.ImageField(blank=True, null=True, upload_to='videos/instructor/'),
        ),
        migrations.AlterField(
            model_name='video',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='videos/thumbnail/'),
        ),
    ]
