# Generated by Django 3.0.6 on 2020-08-09 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20200809_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active_queues',
            field=models.IntegerField(default=0),
        ),
    ]
