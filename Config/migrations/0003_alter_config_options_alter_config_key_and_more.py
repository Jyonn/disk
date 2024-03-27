# Generated by Django 5.0.3 on 2024-03-27 15:29

import SmartDjango.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Config', '0002_auto_20180222_2022'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='config',
            options={'default_manager_name': 'objects'},
        ),
        migrations.AlterField(
            model_name='config',
            name='key',
            field=SmartDjango.models.fields.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='value',
            field=SmartDjango.models.fields.CharField(max_length=255),
        ),
    ]
