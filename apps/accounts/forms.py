from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name  = forms.CharField(max_length=50)

    class Meta:
        model  = User
        fields = ('username','first_name','last_name','email','password1','password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class':'form-control'})

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class':'form-control'})

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name  = forms.CharField(max_length=50, required=False)
    email      = forms.EmailField(required=False)

    class Meta:
        model  = UserProfile
        fields = ('avatar','bio','phone','city','dtm_score','preferred_field','budget_usd')
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in
                   ('phone','city','dtm_score','preferred_field','budget_usd')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class':'form-control'})
        if self.instance and self.instance.user_id:
            u = self.instance.user
            self.fields['first_name'].initial = u.first_name
            self.fields['last_name'].initial  = u.last_name
            self.fields['email'].initial      = u.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        u = profile.user
        u.first_name = self.cleaned_data['first_name']
        u.last_name  = self.cleaned_data['last_name']
        u.email      = self.cleaned_data['email']
        if commit:
            u.save()
            profile.save()
        return profile
