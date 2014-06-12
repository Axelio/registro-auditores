# -*- coding: utf-8 -*-
from django import forms
from django.contrib import auth
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.utils.datastructures import SortedDict
from django.views.decorators.debug import sensitive_post_parameters
from passwords.fields import PasswordField
from captcha.fields import ReCaptchaField
from auditores_suscerte import settings
from auth.models import *

class AuthenticationForm(AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    #captcha = ReCaptchaField()


class CambiarClaveForm(forms.Form):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. "
                                "Please enter it again."),
        'password_mismatch': _("The two password fields didn't match."),
    })

    old_password = forms.CharField(label=_("Old password"))
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                   widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class ValidatingSetPasswordForm(SetPasswordForm):
    new_password1 = PasswordField(label=_("New password"))
    new_password1 = PasswordField(label=_("New password confirmation"))

class ValidatingPasswordChangeForm(PasswordChangeForm):
    new_password1 = PasswordField(label=_("New password"))
