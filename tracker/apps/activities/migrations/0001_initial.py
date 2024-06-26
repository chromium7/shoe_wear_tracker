# Generated by Django 5.0.2 on 2024-04-14 11:15

import django.db.models.deletion
import django.utils.timezone
import tracker.core.model_fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shoes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', tracker.core.model_fields.ChoicesPositiveSmallIntegerField()),
                ('name', models.CharField(blank=True)),
                ('average_pace', models.FloatField(blank=True, null=True)),
                ('distance_covered', models.FloatField(default=0)),
                ('strava_id', models.CharField(blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('shoes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='shoes.shoes')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
