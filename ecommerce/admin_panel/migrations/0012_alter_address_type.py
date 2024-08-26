# Generated by Django 4.2.14 on 2024-08-22 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0011_alter_address_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(choices=[('HOME', 'Home'), ('WORK', 'Work'), ('OTHER', 'Other')], default='HOME', max_length=20, verbose_name='Address type'),
        ),
    ]