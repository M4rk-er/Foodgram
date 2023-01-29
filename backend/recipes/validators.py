import re

from django.core.exceptions import ValidationError

PATTERN = r'^[-a-zA-Z0-9_]+$'


def slug_validation(value):
    if not re.match(PATTERN, value):
        raise ValidationError(
            'Недопустимое значение "slug"'
        )
    return value
