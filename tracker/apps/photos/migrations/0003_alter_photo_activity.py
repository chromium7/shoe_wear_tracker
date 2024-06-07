# Generated by Django 5.0.2 on 2024-05-10 07:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_remove_activity_average_pace_and_more'),
        ('photos', '0002_photo_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='activities.activity'),
        ),
    ]