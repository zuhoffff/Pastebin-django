# Generated by Django 5.0.6 on 2024-05-28 21:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastebin_main_app', '0002_alter_metadata_s3_key'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='metadata',
            table='metadata',
        ),
    ]
