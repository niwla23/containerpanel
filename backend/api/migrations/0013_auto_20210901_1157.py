# Generated by Django 3.2 on 2021-09-01 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20210901_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='max_cpu_usage',
            field=models.FloatField(default=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='server',
            name='max_memory_usage',
            field=models.FloatField(default=4000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='server',
            name='template',
            field=models.CharField(default='none', max_length=100),
            preserve_default=False,
        ),
    ]
