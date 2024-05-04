# Generated by Django 5.0.2 on 2024-04-27 11:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_measurement_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='strava_id',
        ),
        migrations.CreateModel(
            name='StravaProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('athlete_id', models.CharField()),
                ('access_token', models.CharField()),
                ('refresh_token', models.CharField()),
                ('expires_at', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='strava_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]