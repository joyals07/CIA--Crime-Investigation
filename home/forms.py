
from django import forms
from django.contrib.auth.models import User
from .models import Profile  
from .models import CrimeRecord,Person
from .models import Criminal
from django import forms
from .models import Person, Crime

from django import forms
from .models import Person
from django import forms
from django.forms.widgets import DateInput  # Add this import


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'contact','gender','profile_picture']  


class CrimeRecordForm(forms.ModelForm):
    class Meta:
        model = CrimeRecord
        fields = ['person', 'number_of_crimes', 'crimes_done', 'date_committed']
        widgets = {
            'crimes_done': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'date_committed': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # If editing an existing record
            self.fields['person'].disabled = True  # This makes the field non-editable





class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'age', 'address', 'profile_picture']  # Include the fields you want to display in the form


class CrimeForm(forms.ModelForm):
    class Meta:
        model = Crime
        fields = ['crime_type', 'description', 'date_committed', 'location']


class CrimeForm(forms.ModelForm):
    class Meta:
        model = Crime
        fields = ['crime_type', 'description', 'date_committed', 'person']

CRIME_TYPES = [
    ('theft', 'Theft'),
    ('assault', 'Assault'),
    ('fraud', 'Fraud'),
    ('vandalism', 'Vandalism'),
     ('murder','Murder'),
    ('cybercrime','Cybercrime'),
    ('other', 'Other'),
]

class DateInput(forms.DateInput):
    input_type = 'date'  # Ensures the correct HTML5 date input type

class CrimeUpdateForm(forms.ModelForm):
    crime_type = forms.ChoiceField(
        choices=CRIME_TYPES, 
        label="Crime Type", 
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    date_committed = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=DateInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Crime
        fields = ['crime_type', 'description', 'date_committed', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }









class PredictForm(forms.Form):
    time_occ = forms.IntegerField(label="Time Occurred")
    area = forms.IntegerField(label="Area")
    rpt_dist_no = forms.IntegerField(label="Report District Number")
    vict_age = forms.IntegerField(label="Victim Age")
    premis_cd = forms.IntegerField(label="Premises Code")
    weapon_used_cd = forms.IntegerField(label="Weapon Used Code")
    lat = forms.FloatField(label="Latitude")
    lon = forms.FloatField(label="Longitude")

class CrimePredictionForm(forms.Form):
    time_occ = forms.ChoiceField(label="Time Occurred", choices=[], required=True)
    area = forms.ChoiceField(label="Area", choices=[], required=True)
    rpt_dist_no = forms.ChoiceField(label="Report District Number", choices=[], required=True)
    vict_age = forms.ChoiceField(label="Victim Age", choices=[], required=True)
    premis_cd = forms.ChoiceField(label="Premises Code", choices=[], required=True)
    weapon_used_cd = forms.ChoiceField(label="Weapon Used Code", choices=[], required=True)
    lat = forms.FloatField(label="Latitude", required=True, widget=forms.NumberInput(attrs={"placeholder": "Enter Latitude"}))
    lon = forms.FloatField(label="Longitude", required=True, widget=forms.NumberInput(attrs={"placeholder": "Enter Longitude"}))

        

