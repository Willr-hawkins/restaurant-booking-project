from django import forms
from django.utils import timezone

from .models import Booking, Waitlist
from tables.models import Table, TableCombination

INPUT_CLASSES = 'border border-concrete/40 rounded px-3 py-2 w-full focus:outline-none focus:border-maple'

class BookingSearchForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    party_size = forms.IntegerField(min_value=1, max_value=12, initial=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()
    
    def clean_date(self):
        date = self.clean_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError("Please choose a date in the future.")
        return date
    
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
    guest_name = forms.CharField(
        max_length=150, label="Full Name",
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )
    guest_email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': INPUT_CLASSES})
    )
    guest_phone = forms.CharField(
        max_length=30, label="Phone Number",
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES})
    )
    party_size = forms.IntegerField(
        min_value=1, max_value=20,
        widget=forms.NumberInput(attrs={'class': INPUT_CLASSES})
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': INPUT_CLASSES})
    )
    seating_preference = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'No preference'), ('window', 'Window'), ('quiet', 'Quiet'),
            ('patio', 'Patio / Outdoor'), ('bar', 'Bar'),
        ],
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )
    table_override = forms.ChoiceField(
        required=False, label="Table (optional override)",
        widget=forms.Select(attrs={'class': INPUT_CLASSES})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table_override'].choices = build_table_choices()
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError("Please choose a date in the future.")
        return date
    
class WaitlistForm(forms.Form):
    guest_name = forms.CharField(max_length=150, label="Full Name")
    guest_email = forms.EmailField(label="Email")
    guest_phone = forms.CharField(max_length=30, label="Phone Number")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Preferred TIme")
    party_size = forms.IntegerField(min_value=1, max_value=20)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label="Notes (optional)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError("Please choose a date in the future.")
        return date