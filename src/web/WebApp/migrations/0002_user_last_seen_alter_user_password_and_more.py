# Generated by Django 4.1.4 on 2022-12-21 19:44

import WebApp.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, validators=[WebApp.validators.PasswordValidator()], verbose_name='password'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='20 characters or fewer. Letters, digits and ./_ only.', max_length=20, unique=True, validators=[WebApp.validators.UsernameValidator()], verbose_name='username'),
        ),
    ]