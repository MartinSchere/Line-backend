# Generated by Django 2.1.15 on 2020-07-04 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20200704_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='latitude',
            field=models.DecimalField(decimal_places=15, max_digits=18),
        ),
        migrations.AlterField(
            model_name='store',
            name='longitude',
            field=models.DecimalField(decimal_places=15, max_digits=18),
        ),
    ]