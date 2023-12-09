# Generated by Django 4.2 on 2023-11-30 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinar', '0002_alter_webinar_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebinarTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='webinar',
            name='tags',
            field=models.ManyToManyField(related_name='webinars', to='webinar.webinartag'),
        ),
    ]
