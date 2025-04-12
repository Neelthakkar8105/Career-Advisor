from django import forms


class SkillsAssessmentForm(forms.Form):
    """Form for skills assessment questionnaire"""
    # Technical skills (1-5 scale)
    programming = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Programming and coding skills"
    )
    data_analysis = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Data analysis and interpretation"
    )
    design = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Design and visual creativity"
    )
    writing = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Writing and communication"
    )
    project_management = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Project management"
    )
    
    # Soft skills (1-5 scale)
    communication = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Verbal and written communication"
    )
    teamwork = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Teamwork and collaboration"
    )
    leadership = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Leadership and decision making"
    )
    problem_solving = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Problem solving and critical thinking"
    )
    adaptability = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Adaptability and learning"
    )
    
    # Career interests (1-5 scale)
    interest_technology = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Interest in technology and innovation"
    )
    interest_business = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Interest in business and entrepreneurship"
    )
    interest_arts = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Interest in arts and creativity"
    )
    interest_sciences = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Interest in sciences and research"
    )
    interest_helping = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Interest in helping others and society"
    )


class ResumeAnalysisForm(forms.Form):
    """Form for resume analysis"""
    resume_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
        required=False,
        help_text="Paste your resume text here (or we'll use the one from your profile)"
    )
    job_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the job title you're targeting"
    )


class InterviewPrepForm(forms.Form):
    """Form for interview preparation"""
    job_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the job title you're interviewing for"
    )
    company_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Optional: Enter the company name for more tailored advice"
    )
