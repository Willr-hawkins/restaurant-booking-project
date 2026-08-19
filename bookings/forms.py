from django import forms

class BookingSearchForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    party_size = forms.IntegerField(min_value=1, max_value=12, initial=2)
