from django import forms
from apps.deployer.models import Deploy

class DeployAppForm(forms.Form):

    WHAT_TO_DEPLOY = (('all', 'Web+Static'),
                      ('web', 'Web only'),
                      ('static', 'Static only'),)

    password = forms.CharField(widget=forms.PasswordInput, required=True)
    what_to_deploy = forms.ChoiceField(choices=Deploy.TYPE_CHOICES, required=True)
    environment = forms.ChoiceField(choices=Deploy.ENV_CHOICES, required=True)
