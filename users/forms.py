from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelformset_factory
from .models import Profile, Education, WorkExperience, Skill


class UserRegisterForm(UserCreationForm):
    """Form for user registration with extended fields"""
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    """Form for updating User model fields"""
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating Profile model fields"""
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'location', 'current_position', 
                 'desired_position', 'resume', 'linkedin_url', 
                 'github_url', 'portfolio_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'resume': forms.Textarea(attrs={'rows': 6}),
        }


class EducationForm(forms.ModelForm):
    """Form for education details"""
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'current', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class WorkExperienceForm(forms.ModelForm):
    """Form for work experience details"""
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'start_date', 'end_date', 'current', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SkillForm(forms.ModelForm):
    """Form for skills"""
    class Meta:
        model = Skill
        fields = ['name', 'level', 'years_of_experience']


# Create formsets for multiple instances
EducationFormSet = modelformset_factory(
    Education, 
    form=EducationForm,
    extra=1,
    can_delete=True
)

WorkExperienceFormSet = modelformset_factory(
    WorkExperience,
    form=WorkExperienceForm,
    extra=1,
    can_delete=True
)

SkillFormSet = modelformset_factory(
    Skill,
    form=SkillForm,
    extra=3,
    can_delete=True
)
