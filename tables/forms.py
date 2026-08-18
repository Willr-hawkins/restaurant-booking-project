from django import forms
from .models import Table, TableCombination

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'min_covers', 'max_covers', 'section', 'is_fixed']

class TableCombinationForm(forms.ModelForm):
    tables = forms.ModelMultipleChoiceField(
        queryset=Table.objects.filter(is_active=True, is_fixed=False),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = TableCombination
        fields = ['name', 'tables', 'min_covers', 'max_covers']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tables'].initial = self.instance.tables.all()
