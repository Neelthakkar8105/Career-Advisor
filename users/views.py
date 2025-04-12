from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .forms import EducationFormSet, WorkExperienceFormSet, SkillFormSet


def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Handle user profile view and update"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        # Initialize formsets with POST data
        education_formset = EducationFormSet(
            request.POST, 
            prefix='education',
            queryset=request.user.profile.education.all()
        )
        work_formset = WorkExperienceFormSet(
            request.POST, 
            prefix='work',
            queryset=request.user.profile.work_experience.all()
        )
        skill_formset = SkillFormSet(
            request.POST, 
            prefix='skill',
            queryset=request.user.profile.skills.all()
        )
        
        if (u_form.is_valid() and p_form.is_valid() and
            education_formset.is_valid() and work_formset.is_valid() and 
            skill_formset.is_valid()):
            
            u_form.save()
            p_form.save()
            
            # Save formsets
            instances = education_formset.save(commit=False)
            for instance in instances:
                instance.profile = request.user.profile
                instance.save()
            for instance in education_formset.deleted_objects:
                instance.delete()
                
            instances = work_formset.save(commit=False)
            for instance in instances:
                instance.profile = request.user.profile
                instance.save()
            for instance in work_formset.deleted_objects:
                instance.delete()
                
            instances = skill_formset.save(commit=False)
            for instance in instances:
                instance.profile = request.user.profile
                instance.save()
            for instance in skill_formset.deleted_objects:
                instance.delete()
                
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
        # Initialize empty formsets
        education_formset = EducationFormSet(
            prefix='education',
            queryset=request.user.profile.education.all()
        )
        work_formset = WorkExperienceFormSet(
            prefix='work',
            queryset=request.user.profile.work_experience.all()
        )
        skill_formset = SkillFormSet(
            prefix='skill',
            queryset=request.user.profile.skills.all()
        )
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'education_formset': education_formset,
        'work_formset': work_formset,
        'skill_formset': skill_formset,
    }
    
    return render(request, 'users/profile.html', context)
