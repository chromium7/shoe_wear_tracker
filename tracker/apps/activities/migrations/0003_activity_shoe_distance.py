# Generated by Django 5.0.2 on 2024-05-10 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_remove_activity_average_pace_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='shoe_distance',
            field=models.FloatField(blank=True, help_text='in meters', null=True),
        ),
    ]
