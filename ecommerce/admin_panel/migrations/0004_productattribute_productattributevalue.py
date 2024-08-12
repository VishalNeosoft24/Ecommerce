# Generated by Django 4.2.14 on 2024-08-05 06:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin_panel', '0003_coupon_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attribute_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attribute_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_value', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attribute_value_created', to=settings.AUTH_USER_MODEL)),
                ('product_attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attribute_key', to='admin_panel.productattribute')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_attribute_value_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
