# Generated by Django 4.2.14 on 2024-10-22 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0024_usereventtracking_object_info_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usereventtracking',
            name='object_info',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
