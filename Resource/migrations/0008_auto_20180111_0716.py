# Generated by Django 2.0 on 2018-01-11 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Resource', '0007_resource_sub_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=1024, null=True, verbose_name='description in Markdown'),
        ),
    ]
