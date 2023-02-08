# Generated by Django 3.2.16 on 2023-02-06 16:22

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0002_alter_userupload_short_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='userupload',
            name='bbc_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='userupload',
            name='customers',
            field=models.JSONField(blank=True, default=[], null=True),
        ),
        migrations.AddField(
            model_name='userupload',
            name='metering_points',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[], null=True),
        ),
        migrations.AddField(
            model_name='userupload',
            name='sender',
            field=models.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AddField(
            model_name='userupload',
            name='tariffs',
            field=models.JSONField(blank=True, default=[], null=True),
        ),
    ]