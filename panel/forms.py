from django import forms


class PowerActionForm(forms.Form):
    action = forms.CharField()
