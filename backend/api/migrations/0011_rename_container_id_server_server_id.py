# Generated by Django 3.2 on 2021-08-23 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_rename_container_server'),
    ]

    operations = [
        migrations.RenameField(
            model_name='server',
            old_name='container_id',
            new_name='server_id',
        ),
    ]
