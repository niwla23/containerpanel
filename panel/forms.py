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
    name = forms.CharField(label="Technical name (only letters, numbers and underscores)",
                           widget=forms.TextInput(attrs={"class": default_style,
                                                         "placeholder": "mc_speedruns"}))
    description = forms.CharField(
        label="Description (will be shown in panel)",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "Minecraft Speedruns"}))
    image = forms.CharField(
        label="Image",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "itzg/minecraft-server"}))
    env = forms.CharField(
        label="Environment Variables",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "EULA=true;TYPE=AIRPLANE;VERSION=LATEST"}))
    volumes = forms.CharField(
        label="Mounts and volumes",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "./mc:/data;..."}))
    ports = forms.CharField(
        label="Port mappings",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "50451:25565;..."}))
    command_prefix = forms.CharField(
        label="Command prefix",
        widget=forms.TextInput(attrs={"class": default_style, "placeholder": "rcon-cli"}))
    users = forms.MultipleChoiceField(
        label="Users allowed to manage",
        choices=[],
        widget=forms.SelectMultiple(attrs={"class": default_style}))
