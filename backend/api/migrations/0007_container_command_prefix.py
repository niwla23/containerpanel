# Generated by Django 3.2 on 2021-06-01 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_delete_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='container',
            name='command_prefix',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]