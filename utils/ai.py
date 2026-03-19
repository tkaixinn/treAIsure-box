import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_ai(prompt, max_tokens=5000, temperature=0.3):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")

    result = response.json()

    return result["choices"][0]["message"]["content"]

def create_startup_prompt(skills, interests, startup_type, resources):
    """Creates a GPT-ready prompt from user input"""
    return f"""
You are an AI startup advisor. 
Given a person with the following profile, generate 5 unique startup ideas:

Skills: {skills}
Interests: {interests}
Startup Type: {startup_type}
Resources: {resources}

Format: Each idea as a short title and 1-sentence description.
Do NOT number the ideas
"""

def generate_startup_ideas(skills, interests, startup_type, resources):
    """High-level function your Streamlit app will call"""
    prompt = create_startup_prompt(skills, interests, startup_type, resources)
    return call_ai(prompt)

def create_refine_prompt(idea_description, notes):
    return f"""
You are an AI startup mentor. Refine the following idea with the user's notes.
Idea: {idea_description}
User Notes: {notes}

Provide a professional, concise refined idea including:
- Improved description
- 3 actionable next steps
- Suggestions for skills or resources needed
"""
    
def refine_startup_idea(idea_description, notes):
    prompt = create_refine_prompt(idea_description, notes)
    return call_ai(prompt)