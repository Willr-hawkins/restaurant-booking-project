from django import forms
from .models import Table

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'min_covers', 'max_covers', 'section', 'is_fixed']