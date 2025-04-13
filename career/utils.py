import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_resume_nlp(resume_text):
    doc = nlp(resume_text)
    text = resume_text.lower()

    strengths = []
    weaknesses = []

    # Skill-based checks
    if "python" in text:
        strengths.append("Python skill mentioned.")
    else:
        weaknesses.append("Consider including Python if relevant.")

    if "machine learning" in text or "ml" in text:
        strengths.append("Machine Learning is a trending skill—well highlighted.")
    else:
        weaknesses.append("Add Machine Learning skills or projects if applicable.")

    # Experience-based
    if "years" in text or "experience" in text:
        strengths.append("Work experience is well stated.")
    else:
        weaknesses.append("Specify your work experience with durations.")

    # Soft skills
    soft_skills = ["communication", "leadership", "teamwork", "collaboration"]
    found_soft_skills = [skill for skill in soft_skills if skill in text]

    if found_soft_skills:
        strengths.append(f"Soft skills highlighted: {', '.join(found_soft_skills)}")
    else:
        weaknesses.append("Add soft skills to improve overall appeal.")

    # Education check
    if "bachelor" in text or "master" in text or "degree" in text:
        strengths.append("Educational qualifications are clear.")
    else:
        weaknesses.append("Add education details for a complete profile.")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses
    }
