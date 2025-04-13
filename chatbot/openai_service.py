import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful career advisor."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]
