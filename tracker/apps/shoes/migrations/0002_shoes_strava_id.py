# Generated by Django 5.0.2 on 2024-04-16 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoes',
            name='strava_id',
            field=models.CharField(blank=True),
        ),
    ]