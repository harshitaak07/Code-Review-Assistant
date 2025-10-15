from typing import List, Dict
import json
import os
import requests
import re
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = "mistralai/mistral-7b-instruct"
MAX_TOKENS = 500
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_feedback(user_code: str, context: str, model: str = OPENAI_MODEL) -> List[Dict]:
    """
    Generates structured code review feedback using Mistral on OpenRouter.
    Returns a list of dictionaries with fields: line, severity, message, reasoning.
    """
    prompt = f"""
You are a code review assistant. Analyze the following code and provide line-level feedback.
Use the retrieved context to guide your feedback. Respond strictly in JSON format as a list of objects with fields:
- line: line number
- severity: high / medium / low
- message: short description of the issue
- reasoning: explain why this issue has the given severity

Code:
{user_code}

Context:
{context}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert Python code reviewer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": MAX_TOKENS
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return [{
            "line": None,
            "severity": "high",
            "message": f"API error {response.status_code}: {response.text}",
            "reasoning": "The request to OpenRouter failed."
        }]
    try:
        text_output = response.json()["choices"][0]["message"]["content"].strip()
        match = re.search(r"```json\s*(.*?)\s*```", text_output, re.DOTALL)
        if match:
            text_output = match.group(1)
        feedback = json.loads(text_output)
        if not isinstance(feedback, list):
            feedback = [{"line": None, "severity": "medium", "message": str(feedback), "reasoning": "Unexpected response format"}]
        for f in feedback:
            f.setdefault("line", None)
            f.setdefault("severity", "medium")
            f.setdefault("message", "")
            f.setdefault("reasoning", "No reasoning provided")
    except (KeyError, json.JSONDecodeError):
        feedback = [{
            "line": None,
            "severity": "medium",
            "message": text_output,
            "reasoning": "Failed to parse JSON from model output"
        }]
    return feedback
