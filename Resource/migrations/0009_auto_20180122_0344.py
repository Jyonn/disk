# Generated by Django 2.0 on 2018-01-22 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Resource', '0008_auto_20180111_0716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='create_time',
            field=models.DateTimeField(auto_created=True),
        ),
    ]
