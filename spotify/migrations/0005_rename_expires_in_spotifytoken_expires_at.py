# Generated by Django 3.2.7 on 2021-10-11 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0004_alter_spotifytoken_access_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spotifytoken',
            old_name='expires_in',
            new_name='expires_at',
        ),
    ]
