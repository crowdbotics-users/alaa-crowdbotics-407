# Generated by Django 2.1.2 on 2018-10-08 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='verification_metadata',
            field=models.TextField(blank=True),
        ),
    ]
