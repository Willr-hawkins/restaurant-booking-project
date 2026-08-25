from django import forms

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
    