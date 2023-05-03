# Generated by Django 4.2 on 2023-05-03 05:16

import WebApp.validators
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(error_messages={'unique': 'Another user with that username already exists.'}, help_text='20 characters or fewer. Letters, digits and ./_ only.', max_length=20, unique=True, validators=[WebApp.validators.UsernameValidator(), WebApp.validators.ForbiddenWordsValidator()], verbose_name='username')),
                ('password', models.CharField(max_length=128, validators=[WebApp.validators.PasswordValidator()], verbose_name='Password')),
                ('grade', models.IntegerField(choices=[(9, '9'), (10, '10'), (11, '11'), (12, '12')], default=9)),
                ('pronouns', models.CharField(choices=[('he/him', 'he/him'), ('she/her', 'she/her'), ('they/them', 'they/them'), ('Prefer Not To Say', 'Prefer Not To Say')], default='Prefer Not To Say', max_length=20)),
                ('school', models.CharField(default='', max_length=100)),
                ('user_bio', models.TextField(default='', max_length=1000, validators=[WebApp.validators.ForbiddenWordsValidator()])),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('recent_calls', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='QueueItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interests', models.JSONField(default=list)),
                ('preferred_grade', models.IntegerField(choices=[(9, 9), (10, 10), (11, 11), (12, 12), (0, 'No Preference')], default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('user1_in_room', models.BooleanField(default=False)),
                ('user2_in_room', models.BooleanField(default=False)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
