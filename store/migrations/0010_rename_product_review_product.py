# Generated by Django 4.1.7 on 2023-03-22 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0009_rename_descriptions_review_description"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review",
            old_name="Product",
            new_name="product",
        ),
    ]
