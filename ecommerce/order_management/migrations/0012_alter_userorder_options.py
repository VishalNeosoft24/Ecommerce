# Generated by Django 4.2.14 on 2024-10-15 06:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order_management', '0011_remove_paymentgateway_payment_order_id_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userorder',
            options={'ordering': ['-created_at']},
        ),
    ]
