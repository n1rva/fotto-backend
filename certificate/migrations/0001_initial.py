# Generated by Django 4.2 on 2023-10-23 22:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webinar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=10, unique=True)),
                ('certificate_file', models.FileField(upload_to='certificates/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('webinar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webinar.webinar')),
            ],
            options={
                'unique_together': {('user', 'webinar')},
            },
        ),
    ]
