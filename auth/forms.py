# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate, get_user_model
from auth.models import *
from django.utils.translation import ugettext_lazy as _

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
        'user_not_exists': _("Este usuario no existe."),
    }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username:
            usuarios = UserProfile.objects.filter(user__username__iexact=username)
            if not usuarios.exists():
                raise forms.ValidationError(
                    self.error_messages['user_not_exists'],
                    code='user_not_exists',
                    params={'username': get_user_model()._meta.get_field(get_user_model().USERNAME_FIELD)},
                )
            else:
                usuario = usuarios[0]
                if not usuario.user.is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='user_not_exists',
                        params={'username': get_user_model()._meta.get_field(get_user_model().USERNAME_FIELD)},
                    )
        return self.cleaned_data

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            usuarios = UserProfile
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
