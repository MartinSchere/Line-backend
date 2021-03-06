# Generated by Django 3.0.6 on 2020-08-04 18:06

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200801_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='opening_days',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Mo', 'Monday'), ('Tu', 'Tuesday'), ('We', 'Wendnesday'), ('Th', 'Monday'), ('Fr', 'Friday'), ('Sa', 'Saturday'), ('Su', 'Sunday')], max_length=2),
        ),
    ]
