# Generated by Django 4.2.3 on 2023-07-25 19:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('webhook_listener', '0002_alter_boardingprocess_netbox_device_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardingprocess',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='boardingprocess',
            name='date_modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
