# Generated by Django 3.2.8 on 2021-11-08 18:36

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20211014_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='server_id',
            field=models.CharField(default=api.models.create_id, editable=False, max_length=16, primary_key=True, serialize=False, unique=True),
        ),
    ]