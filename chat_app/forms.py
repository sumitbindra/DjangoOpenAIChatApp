from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [ 'child_name', 'robot_name', 'mom_name', 'dad_name', 'pet_name']