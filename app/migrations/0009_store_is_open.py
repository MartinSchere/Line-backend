# Generated by Django 2.1.15 on 2020-07-10 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20200706_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='is_open',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
