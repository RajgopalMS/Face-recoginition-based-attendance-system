# Generated by Django 2.1.5 on 2019-01-28 03:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Sample', '0004_attend'),
    ]

    operations = [
        migrations.AddField(
            model_name='attend',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
