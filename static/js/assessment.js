/**
 * Assessment.js - Handles the skills assessment navigation and functionality
 */

/**
 * Initializes the navigation for the skills assessment form
 */
function initAssessmentNavigation() {
    const form = document.getElementById('skillsAssessmentForm');
    if (!form) return;
    
    const techSkillsSection = document.getElementById('technical-skills-section');
    const softSkillsSection = document.getElementById('soft-skills-section');
    const interestsSection = document.getElementById('interests-section');
    const progressBar = document.getElementById('assessmentProgress');
    
    const sections = [techSkillsSection, softSkillsSection, interestsSection];
    let currentSectionIndex = 0;
    
    // Update the progress bar
    function updateProgress() {
        const progress = ((currentSectionIndex) / (sections.length - 1)) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    // Switch to the next section
    function goToNextSection() {
        if (currentSectionIndex < sections.length - 1) {
            // Hide current section
            sections[currentSectionIndex].classList.add('d-none');
            
            // Show next section
            currentSectionIndex++;
            sections[currentSectionIndex].classList.remove('d-none');
            
            // Update progress
            updateProgress();
            
            // Scroll to top of the form
            form.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Switch to the previous section
    function goToPreviousSection() {
        if (currentSectionIndex > 0) {
            // Hide current section
            sections[currentSectionIndex].classList.add('d-none');
            
            // Show previous section
            currentSectionIndex--;
            sections[currentSectionIndex].classList.remove('d-none');
            
            // Update progress
            updateProgress();
            
            // Scroll to top of the form
            form.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Add event listeners to the next buttons
    document.querySelectorAll('.next-section').forEach(button => {
        button.addEventListener('click', function() {
            // Validate the current section before proceeding
            if (validateCurrentSection()) {
                goToNextSection();
            }
        });
    });
    
    // Add event listeners to the previous buttons
    document.querySelectorAll('.prev-section').forEach(button => {
        button.addEventListener('click', goToPreviousSection);
    });
    
    // Validate the current section's inputs
    function validateCurrentSection() {
        const currentSection = sections[currentSectionIndex];
        const radioGroups = currentSection.querySelectorAll('.skill-rating');
        let isValid = true;
        
        radioGroups.forEach(group => {
            const checkedRadio = group.querySelector('input[type="radio"]:checked');
            if (!checkedRadio) {
                isValid = false;
                
                // Add visual indication that this needs to be filled
                group.classList.add('is-invalid');
                
                // Create error message if it doesn't exist
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'Please select a rating for this skill';
                
                // Only add the error message if it doesn't already exist
                if (!group.nextElementSibling || !group.nextElementSibling.classList.contains('invalid-feedback')) {
                    group.parentNode.insertBefore(errorDiv, group.nextElementSibling);
                }
            } else {
                // Remove any error indication
                group.classList.remove('is-invalid');
                if (group.nextElementSibling && group.nextElementSibling.classList.contains('invalid-feedback')) {
                    group.parentNode.removeChild(group.nextElementSibling);
                }
            }
        });
        
        return isValid;
    }
    
    // Add event listeners to radio buttons to clear validation errors when selected
    document.querySelectorAll('.skill-rating input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const group = this.closest('.skill-rating');
            group.classList.remove('is-invalid');
            
            if (group.nextElementSibling && group.nextElementSibling.classList.contains('invalid-feedback')) {
                group.parentNode.removeChild(group.nextElementSibling);
            }
        });
    });
    
    // Form submission validation
    form.addEventListener('submit', function(event) {
        // Validate the current section
        if (!validateCurrentSection()) {
            event.preventDefault();
            return false;
        }
        
        // If we're not on the last section, prevent submission and go to next section
        if (currentSectionIndex < sections.length - 1) {
            event.preventDefault();
            goToNextSection();
            return false;
        }
        
        // Otherwise, allow the form to submit
        return true;
    });
    
    // Initialize progress
    updateProgress();
}

/**
 * Formats assessment results for display
 * @param {Object} results - The assessment results object
 */
function formatAssessmentResults(results) {
    if (!results) return;
    
    // Format technical skills
    const technicalSkills = results.technical_skills;
    const technicalLabels = Object.keys(technicalSkills).map(key => {
        return key.replace('_', ' ').charAt(0).toUpperCase() + key.replace('_', ' ').slice(1);
    });
    const technicalData = Object.values(technicalSkills);
    
    // Format soft skills
    const softSkills = results.soft_skills;
    const softLabels = Object.keys(softSkills).map(key => {
        return key.charAt(0).toUpperCase() + key.slice(1);
    });
    const softData = Object.values(softSkills);
    
    // Format interests
    const interests = results.interests;
    const interestLabels = Object.keys(interests).map(key => {
        return key.replace('interest_', '').charAt(0).toUpperCase() + key.replace('interest_', '').slice(1);
    });
    const interestData = Object.values(interests);
    
    return {
        technical: { labels: technicalLabels, data: technicalData },
        soft: { labels: softLabels, data: softData },
        interests: { labels: interestLabels, data: interestData }
    };
}
