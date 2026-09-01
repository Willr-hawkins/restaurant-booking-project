from django import forms

from .models import Booking
from tables.models import Table, TableCombination

class BookingSearchForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    party_size = forms.IntegerField(min_value=1, max_value=12, initial=2)


class GuestDetailsForm(forms.Form):
    guest_name = forms.CharField(max_length=150, label="Full Name")
    guest_email = forms.EmailField(label="Email")
    guest_phone = forms.CharField(max_length=30, label="Phone Number")
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Special Requests (allergies, dietary needs, occasion)",
    )
    seating_preference = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'No preference'),
            ('window', 'Window'),
            ('quiet', 'Quiet'),
            ('patio', 'Patio / Outdoor'),
            ('bar', 'Bar'),
        ],
        label="Seating Preference",
    )


class BookingModifyForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['special_requests', 'seating_preference']

def build_table_choices():
    choices = [('', 'Auto-assign (recommended)')]
    for t in Table.objects.filter(is_active=True):
        choices.append((f'table:{t.id}', f'{t.name} ({t.min_covers}-{t.max_covers})'))
    for c in TableCombination.objects.filter(is_active=True):
        choices.append((f'combo:{c.id}', f'{c} ({c.min_covers}-{c.max_covers})'))
    return choices

class PhoneBookingForm(forms.Form):
    guest_name = forms.CharField(max_length=150, label="Full Name")
    guest_email = forms.EmailField(label="Email")
    guest_phone = forms.CharField(max_length=30, label="Phone Number")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    party_size = forms.IntegerField(min_value=1, max_value=20)
    specail_requests = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    seating_preference = forms.ChoiceField(required=False, choices=[
        ('', 'No preference'), ('window', 'Window'), ('quiet', 'Quiet'),
        ('patio', 'Patio / Outdoor'), ('bar', 'Bar'),
    ])
    table_override = forms.ChoiceField(required=False, label="Table (optional override)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table_override'].choices = build_table_choices()