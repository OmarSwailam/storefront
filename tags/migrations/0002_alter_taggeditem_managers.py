# Generated by Django 4.1.7 on 2023-03-18 10:50

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='taggeditem',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
