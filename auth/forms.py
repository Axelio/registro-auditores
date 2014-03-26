# -*- coding: utf-8 -*-
from django import forms
from django.contrib import auth
from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.utils.datastructures import SortedDict
from django.views.decorators.debug import sensitive_post_parameters
from passwords.fields import PasswordField
from auditores_suscerte import settings
from auth.models import *

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(label="Usuario", max_length=254, widget = forms.TextInput(attrs={'type':'text', 'class':'input-block-level', 'required':'required', 'placeholder':_('User')}))
    password = forms.CharField(max_length=200, widget = forms.PasswordInput(attrs={'type':'password', 'class':'input-block-level','required':'required','placeholder':_('Password')}))

    error_messages = {
        'invalid_login': _(u"Usuario y/o contraseña inválido. "
                           u"Note que ambos campos pueden ser sensibles a mayúsculas."),
        'inactive': _("This account is inactive."),
    }
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': get_user_model()._meta.get_field(get_user_model().USERNAME_FIELD)},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

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
