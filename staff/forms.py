from django import forms
from django.contrib.auth.forms import AuthenticationForm

INPUT_CLASSES = 'border border-concrete/40 rounded px-3 py-2 w-full focus:outline-none focus:border-maple'


class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES})
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Please enter a correct username and password.",
        'not_staff': "This account does not have staff access.",
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not hasattr(user, 'staff_profile'):
            raise forms.ValidationError(
                self.error_messages['not_staff'],
                code='not_staff',
            )