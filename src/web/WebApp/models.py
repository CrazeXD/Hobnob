from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import UsernameValidator, PasswordValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
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
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "grade", "pronouns", "password"]