# Generated by Django 5.0.2 on 2025-03-27 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.FileField(upload_to='files/'),
        ),
    ]
