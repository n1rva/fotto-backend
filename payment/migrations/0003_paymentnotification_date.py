# Generated by Django 4.2 on 2023-12-05 22:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_paymentnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentnotification',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
