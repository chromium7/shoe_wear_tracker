# Generated by Django 5.0.2 on 2024-05-04 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='average_pace',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='distance_covered',
        ),
        migrations.AddField(
            model_name='activity',
            name='distance',
            field=models.FloatField(default=0, help_text='in meters'),
        ),
        migrations.AddField(
            model_name='activity',
            name='duration',
            field=models.IntegerField(blank=True, help_text='in seconds', null=True),
        ),
    ]
