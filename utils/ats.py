import re
from PyPDF2 import PdfReader

def extract_text(file_path):

    # ✅ PDF support
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

        return text.lower()

    # ✅ TXT support (fallback)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().lower()

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return set(words)


def analyze_resume(file_path, jd_text):

    resume_text = extract_text(file_path)
    jd_text = jd_text.lower()

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    # 🎯 Matching Skills
    matched = resume_keywords.intersection(jd_keywords)

    # ❌ Missing Skills
    missing = jd_keywords - resume_keywords

    # 📊 ATS SCORE
    score = int((len(matched) / len(jd_keywords)) * 100) if jd_keywords else 0

    # 💡 Suggestions
    suggestions = []

    if score < 40:
        suggestions.append("Your resume needs significant improvement. Add more relevant skills.")
    elif score < 70:
        suggestions.append("Good resume, but you are missing some important keywords.")
    else:
        suggestions.append("Excellent resume! Well optimized for ATS.")

    if len(missing) > 0:
        suggestions.append("Include missing skills from job description.")

    if "project" not in resume_text:
        suggestions.append("Add project section to strengthen your resume.")

    if "experience" not in resume_text:
        suggestions.append("Mention experience or internships.")

    return {
        "score": score,
        "matched": list(matched)[:15],
        "missing": list(missing)[:15],
        "suggestions": suggestions
    }