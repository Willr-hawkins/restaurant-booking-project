from django import forms
from .models import Table, TableCombination

INPUT_CLASSES = 'border border-concrete/40 rounded px-3 py-2 w-full focus:outline-none focus:border-maple'

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'min_covers', 'max_covers', 'section', 'is_fixed']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'min_covers': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'max_covers': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'section': forms.Select(attrs={'class': INPUT_CLASSES}),
            'is_fixed': forms.CheckboxInput(attrs={'class': 'rounded border-concrete/40'}),
        }

class TableCombinationForm(forms.ModelForm):
    tables = forms.ModelMultipleChoiceField(
        queryset=Table.objects.filter(is_active=True, is_fixed=False),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = TableCombination
        fields = ['name', 'tables', 'min_covers', 'max_covers']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'min_covers': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'max_covers': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tables'].initial = self.instance.tables.all()
