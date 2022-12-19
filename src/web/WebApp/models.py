from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # add additional fields here
    #Create 4 choices for grade, 9-12
    grade_choices = (
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
    )
    #Create a field for those choices
    grade = models.IntegerField(choices=grade_choices, default=9)
    #Create a field for the persons pronouns with choices (he/him, she/her, they/them, prefer not to say)
    pronoun_choices = (
        ('he/him', 'he/him'),
        ('she/her', 'she/her'),
        ('they/them', 'they/them'),
        ('Prefer Not To Say', 'Prefer Not To Say'),
    )
    pronouns = models.CharField(choices=pronoun_choices, max_length=20, default='Prefer Not To Say')
    
