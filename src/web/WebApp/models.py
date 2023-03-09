from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import UsernameValidator, PasswordValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    def __str__(self):
        return self.username
    username_validator = UsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=20,
        unique=True,
        help_text=_(
            "20 characters or fewer. Letters, digits and ./_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    password_validator = PasswordValidator()
    password = models.CharField(
        _("password"),
        max_length=128,
        validators=[password_validator]
    )
    grade_choices = (
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
    )
    grade = models.IntegerField(choices=grade_choices, default=9)
    pronoun_choices = (
        ('he/him', 'he/him'),
        ('she/her', 'she/her'),
        ('they/them', 'they/them'),
        ('Prefer Not To Say', 'Prefer Not To Say'),
    )
    pronouns = models.CharField(
        choices=pronoun_choices,
        max_length=20,
        default='Prefer Not To Say'
    )
    school = models.CharField(max_length=100, default='')
    recent_calls = models.ManyToManyField('self', blank=True, symmetrical=False)
    in_queue = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email", "first_name", "last_name",
                       "grade", "pronouns", "school", "password"]


class QueueItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ChatRoom(models.Model):
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user2')
    room_id = models.AutoField(primary_key=True)
    room_url = models.CharField(max_length=100, default='')
