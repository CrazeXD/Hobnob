# Generated by Django 4.2.1 on 2023-05-15 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0003_chatroom_call_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='exp',
            field=models.IntegerField(default=0),
        ),
    ]
