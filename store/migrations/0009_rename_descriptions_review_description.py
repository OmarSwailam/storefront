# Generated by Django 4.1.7 on 2023-03-22 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0008_review"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review",
            old_name="descriptions",
            new_name="description",
        ),
    ]
