from django.contrib import admin
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import GroupAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from usercenter.models import MyUser


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        # fields = ('username',)
        fields = '__all__'

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    # password = ReadOnlyPasswordHashField()
    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("Raw passwords are not stored, so there is no way to see "
                                                    "this user's password, but you can change the password "
                                                    "using <a href=\"../password/\">this form</a>."))
    class Meta:
        model = MyUser
        # fields = ('username', 'password', 'is_active','is_admin','is_superuser')
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'alias','is_staff', 'is_admin','email','create_date','gender',)
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ("alias","email",'gender',)}),
        ('Permissions', {'fields': ('is_active','is_admin','is_superuser','is_staff','user_permissions','groups','jenkins_job',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2','email','gender','jenkins_job',)}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ('user_permissions','groups','jenkins_job',)

# class GroupAdmin(admin.ModelAdmin):
#     filter_horizontal = ('permissions',)


class GroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=MyUser.objects.all(),
                                           widget=FilteredSelectMultiple('Users', False),
                                           required=False)
    class Meta:
        model = Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['users'] = instance.user_set.all()
            kwargs['initial'] = initial
        super(GroupAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        group = super(GroupAdminForm, self).save(commit=commit)

        if commit:
            group.user_set = self.cleaned_data['users']
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                group.user_set = self.cleaned_data['users']
            self.save_m2m = new_save_m2m
        return group

class MyGroupAdmin(GroupAdmin):
    form = GroupAdminForm
    filter_horizontal = ('jenkins_job','permissions')

    fieldsets = (
        (None, {'fields': ('name','alias',)}),
        (None, {'fields': ('permissions','users','jenkins_job')}),
    )

# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)
