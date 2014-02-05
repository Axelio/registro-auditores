# -*- coding: UTF8 -*-
from django.contrib import admin
from auth.models import UserProfile
from django.contrib.auth.admin import UserAdmin, User
from django.utils.translation import ugettext_lazy as _

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model=UserProfile
    can_delete=False 
    extra=1


class UserProfileAdmin(UserAdmin):
    search_fields=['userprofile__persona__num_identificacion','username','email',]
    inlines=[UserProfileInline, ]    
    staff_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'),{'fields':('groups',) })
    )
    staff_fieldsets_sinpass = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'),{'fields':('groups',) })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    def queryset(self,request):
        qs=super(UserProfileAdmin,self).queryset(request)
        if not request.user.is_superuser:
            qs=qs.exclude(is_superuser=True)
        return qs
    ''' Para poder obtener el usuario desde el formulario UserFormChange definimos la variable aqui'''
    def get_form(self, request, obj=None, **kwargs):
        form = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        ''' Si se esta editando el mismo usuario  y no es superusuario se muestran los grupos a los que pertenece el usuario, si no es el mismo usuario solo muestra estudiantes '''
        '''
        if not request.user.is_superuser:
            from django.db.models import Q 
            if obj==request.user:
                form.base_fields['groups'].queryset=(grupos|request.user.groups.all()).distinct()
            else:
                form.base_fields['groups'].queryset=grupos
        '''
        return form
    
    ''' Evita escalabilidad de privilegios cuando  un usuario staff NO superUsuario intente cambiar la clave de un SuperUsuario. '''
    from django.views.decorators.debug import sensitive_post_parameters
    @sensitive_post_parameters()
    def user_change_password(self,request,id,form_url=''):
        if not  request.user.is_superuser and self.queryset(request).get(pk=id).is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        else:
            return super(UserProfileAdmin,self).user_change_password(request,id,form_url)

    
    ''' No mostrar la opción de SuperUsuario si no se es un superusuario. Evitar bug de escalabilida de permisos
    '''
    def change_view(self, request, *args, **kwargs):
        # for non-superuser
        if not request.user.is_superuser:
            try:
                #Si el usuario editado es un SuperUsuario y el editor no lo es,o Si el usuario editado es staff  NO se muestra el enlace de cambiar clave. Evitando escalabilidad de privilegios
                
                if self.queryset(request).get(pk=args[0]).is_superuser or self.queryset(request).get(pk=args[0]).is_staff:
                    self.fieldsets=self.staff_fieldsets_sinpass
                else:
                    self.fieldsets = self.staff_fieldsets
                ''' Se limita los grupos disponibles a los que posee el usuario y a Estudiante'''
                response = super(UserAdmin,self).change_view( request, *args, **kwargs)

                #response = super(UserAdmin,self).change_view( request, *args, **kwargs)
            finally:
                # Reset fieldsets to its original value
                self.fieldsets = super( UserAdmin,self).fieldsets
            return response
        else:
            return super(UserAdmin,self).change_view( request, *args, **kwargs)

admin.site.unregister(User)
admin.site.register(User,UserProfileAdmin)
