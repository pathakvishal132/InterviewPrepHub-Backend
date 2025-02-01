# Generated by Django 5.1 on 2025-01-27 08:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='questions',
            name='problem_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='questions',
            name='submission_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='user_id',
            field=models.IntegerField(default=0),
        ),
    ]
