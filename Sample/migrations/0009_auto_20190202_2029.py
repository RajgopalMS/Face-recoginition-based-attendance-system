# Generated by Django 2.1.5 on 2019-02-02 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sample', '0008_attend_cid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attend',
            name='cid',
            field=models.IntegerField(max_length=100),
        ),
    ]
