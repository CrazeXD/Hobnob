from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z0-9_.]*$"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and _/. characters."
    )

@deconstructible
class PasswordValidator(validators.RegexValidator):
    regex = r"^(?=[^~`]*[~`])(?=[^,]*[,])[^~`,]{8,}$"
    message = _(
        "Enter a valid password. This value may contain any characters except ~, `, and , and must be greater than 8 units."
    )
