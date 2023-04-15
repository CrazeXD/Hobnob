from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from Hobnob.settings import BASE_DIR

words = open(BASE_DIR / "assets/innapropriatenames.txt", "r").read().replace("_", "").replace(".", "").splitlines()
class ForbiddenWordsValidator(validators.BaseValidator):
    """
    Custom validator that checks if any words from a list are present in a username.
    """

    def __init__(self):
        self.forbidden_words = words

    def __call__(self, value):
        """
        Validate that no forbidden words are present in the username.
        """
        for word in self.forbidden_words:
            if word.lower() in value.lower():
                raise ValidationError(
                    f"Forbidden word '{word}'",
                    code='forbidden_word',
                )

    def __eq__(self, other):
        """
        Custom equality method to compare validators by their forbidden_words list.
        """
        return (
            isinstance(other, ForbiddenWordsValidator) and
            self.forbidden_words == other.forbidden_words
        )

@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z0-9_.]*$"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and _/. characters."
    )

@deconstructible
class PasswordValidator(validators.RegexValidator):
    # Create a regex expression that can contain any character except for a space, ~, `, and , and must be at least 8 characters long
    regex = r"^[^\s~`,]{8,}$"
    message = _(
        "Enter a valid password. This value may contain any characters except ~, `, and , and must be greater than 8 units."
    )

