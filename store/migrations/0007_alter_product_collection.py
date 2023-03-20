# Generated by Django 4.1.7 on 2023-03-20 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_orderitem_product_alter_product_promotions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='store.collection'),
        ),
    ]
