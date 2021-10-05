from django import forms
from django.contrib.auth.models import User

default_style = "pl-2 bg-gray-800 rounded-md w-full mb-2"


class PowerActionForm(forms.Form):
    action = forms.CharField()


def patch_form_with_users(form):
    form.fields["users"].choices = [(o.id, str(o)) for o in User.objects.filter()]
    return form


def get_create_container_form(initial=None):
    form = patch_form_with_users(CreateContainerForm(initial=initial))
    return form


class CreateContainerForm(forms.Form):
    template = forms.CharField(label="Template",
                               widget=forms.HiddenInput())
    name = forms.CharField(label="Technical name (only letters, numbers and underscores)",
                           widget=forms.TextInput(attrs={"class": default_style,
                                                         "placeholder": "mc_speedruns"}))
    description = forms.CharField(
        label="Description (will be shown in api)",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "Minecraft Speedruns"}))
    env = forms.CharField(
        label="Environment Variables",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "EULA=true;TYPE=AIRPLANE;VERSION=LATEST"}))
    ports = forms.CharField(
        label="Port mappings",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "50451:25565;..."}))
    sftp_port = forms.CharField(label="SFTP Port",
                                widget=forms.TextInput(attrs={"class": default_style, "placeholder": "40043"}))
    sftp_password = forms.CharField(label="SFTP Password", widget=forms.TextInput(
        attrs={"class": default_style, "placeholder": "test123!*'#+d22"}))
    users = forms.MultipleChoiceField(
        label="Users allowed to manage",
        choices=[],
        widget=forms.SelectMultiple(attrs={"class": default_style}))
