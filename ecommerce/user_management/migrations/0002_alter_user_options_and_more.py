# Generated by Django 4.2.14 on 2024-11-05 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['username'], name='user_manage_usernam_04b498_idx'),
        ),
    ]
