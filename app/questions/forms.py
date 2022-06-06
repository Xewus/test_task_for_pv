from django import forms
from .models import Results


class ResuktForm(forms.ModelForm):
    class Meta:
        model = Results
        fields = ('aswers',)
