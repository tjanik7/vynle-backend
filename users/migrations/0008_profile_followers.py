# Generated by Django 3.2.21 on 2023-10-29 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20230916_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='followers',
            field=models.ManyToManyField(related_name='_users_profile_followers_+', to='users.Profile'),
        ),
    ]
