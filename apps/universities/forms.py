from django import forms
from .models import University, Faculty

class UniversityForm(forms.ModelForm):
    class Meta:
        model  = University
        exclude = ('slug', 'created_at', 'updated_at')
        widgets = {
            'name':        forms.TextInput(attrs={'class':'form-control'}),
            'short_name':  forms.TextInput(attrs={'class':'form-control'}),
            'city':        forms.Select(attrs={'class':'form-select'}),
            'uni_type':    forms.Select(attrs={'class':'form-select'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'website':     forms.URLInput(attrs={'class':'form-control'}),
            'application_link': forms.URLInput(attrs={'class':'form-control'}),
            'founded_year': forms.NumberInput(attrs={'class':'form-control'}),
            'ranking':     forms.NumberInput(attrs={'class':'form-control'}),
            'total_students': forms.NumberInput(attrs={'class':'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

class FacultyForm(forms.ModelForm):
    class Meta:
        model  = Faculty
        exclude = ('created_at',)
        widgets = {
            'university':  forms.Select(attrs={'class':'form-select'}),
            'name':        forms.TextInput(attrs={'class':'form-control'}),
            'field':       forms.TextInput(attrs={'class':'form-control'}),
            'quota_2024':  forms.NumberInput(attrs={'class':'form-control'}),
            'quota_2025':  forms.NumberInput(attrs={'class':'form-control'}),
            'min_score':   forms.NumberInput(attrs={'class':'form-control'}),
            'max_score':   forms.NumberInput(attrs={'class':'form-control'}),
            'tuition_usd': forms.NumberInput(attrs={'class':'form-control'}),
            'deadline':    forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'requirements': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'duration_years': forms.NumberInput(attrs={'class':'form-control'}),
            'language':    forms.TextInput(attrs={'class':'form-control'}),
            'degree_type': forms.TextInput(attrs={'class':'form-control'}),
        }

class SearchForm(forms.Form):
    q         = forms.CharField(required=False, widget=forms.TextInput(
                    attrs={'class':'form-control','placeholder':'Search universities or programs…'}))
    city      = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class':'form-select'}))
    uni_type  = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class':'form-select'}))
    field     = forms.CharField(required=False, widget=forms.TextInput(
                    attrs={'class':'form-control','placeholder':'Field of study…'}))
    min_score = forms.IntegerField(required=False, widget=forms.NumberInput(
                    attrs={'class':'form-control','placeholder':'Your DTM score'}))
    max_tuition = forms.IntegerField(required=False, widget=forms.NumberInput(
                    attrs={'class':'form-control','placeholder':'Max tuition USD/year'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import CITY_CHOICES, TYPE_CHOICES
        self.fields['city'].choices    = [('','All Cities')]    + list(CITY_CHOICES)
        self.fields['uni_type'].choices = [('','All Types')]   + list(TYPE_CHOICES)
