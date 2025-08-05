import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Custom Validator that Validates that the password contains at least one lowercase letter,
# one uppercase letter, and one special character.

class ComplexPasswordValidator:

    def validate(self, password, user=None):
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('This password must contain at least one lowercase letter.'),
                code='password_no_lowercase',
            )
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('This password must contain at least one uppercase letter.'),
                code='password_no_uppercase',
            )
        
        # Check for at least one special character (e.g., !@#$%^&*()_+\-=\[\]{}|;:,.<>?/~)
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/~]', password):
            raise ValidationError(
                _('This password must contain at least one special character.'),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            'Your password must contain at least one lowercase letter, '
            'one uppercase letter, and one special character.'
        )