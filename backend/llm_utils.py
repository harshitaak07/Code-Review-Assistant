"""
LLM Utilities for Code Review Assistant
Purpose:
    - Take user code + retrieved context
    - Generate structured feedback
"""

from typing import List, Dict
import json

import openai
OPENAI_MODEL = "gpt-4"  # or gpt-3.5-turbo
MAX_TOKENS = 500

def generate_feedback(user_code: str, context: str, model: str = OPENAI_MODEL) -> List[Dict]:
    prompt = f""" 
You are a code review assistant. Analyze the following code and provide line-level feedback. 
Use the retrieved context to guide your feedback. Respond in JSON format as a list of objects with fields:
- line: line number
- severity: high / medium / low
- message: short description of the issue
Code: {user_code}
Context: {context}
"""
    response = openai.ChatCompletion.create(
            model = model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=MAX_TOKENS
        )
    text_output = response.choices[0].message.content.strip()
    try:
        feedback = json.loads(text_output)
    except json.JSONDecodeError:
        feedback = [{"line": None, "severity": "medium", "message": text_output}]
    return feedback

