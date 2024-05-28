# Generated by Django 5.0.6 on 2024-05-28 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.CharField(max_length=20)),
                ('user_agent', models.CharField(max_length=80)),
                ('s3_key', models.CharField(max_length=80, unique=True)),
                ('key_usages', models.IntegerField(default=0)),
            ],
        ),
    ]
