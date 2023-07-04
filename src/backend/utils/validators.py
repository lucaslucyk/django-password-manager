from keyword import iskeyword
from django.utils.deconstruct import deconstructible
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


@deconstructible
class KeywordValidator:

    def __init__(self, message=None):
        self.message = message or _("Invalid Keyword")

    def __call__(self, value):
        if not value.isidentifier() or iskeyword(value):
            raise ValidationError(
                message=self.message,
                params={'value': value},
            )


@deconstructible
class URLValidatorWithoutDomain:
    
    def __init__(self, message=None):
        self.regex = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+/(?:[-\w.]|(?:%[\da-fA-F]{2}))+/?$'
        self.message = message or _('Invalid URL')

    def __call__(self, value):
        validator = RegexValidator(
            regex=self.regex,
            message=self.message,
        )
        validator(value)

