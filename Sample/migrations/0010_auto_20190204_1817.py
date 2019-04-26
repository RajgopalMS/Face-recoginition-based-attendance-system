# Generated by Django 2.1.5 on 2019-02-04 12:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Sample', '0009_auto_20190202_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='cources',
            name='faceimage',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='upload/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cources',
            name='fmail',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cources',
            name='phno',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attend',
            name='cid',
            field=models.IntegerField(),
        ),
    ]
