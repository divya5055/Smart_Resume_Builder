from openai import OpenAI

client = OpenAI(api_key="OPENAI_API_KEY")

def enhance_text(prompt_text, section_type):
    prompt = f"""
    Improve the following {section_type} for a professional resume.
    Make it clear, concise, ATS-friendly, and impactful.

    Original Text:
    {prompt_text}

    Enhanced Version:
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()