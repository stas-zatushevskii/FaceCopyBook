# Generated by Django 4.1.5 on 2023-01-07 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatar.jpg', upload_to='avatars/'),
        ),
    ]
