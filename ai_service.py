import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyse_business_message(message: str):
    prompt = f"""
You are an AI business automation assistant.

Analyse this customer/business message:

"{message}"

Return ONLY valid JSON with this structure:
{{
  "category": "sales | support | complaint | follow_up | admin | unknown",
  "priority": "low | medium | high",
  "reply": "professional email-style response"
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    text = response.output_text

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "category": "unknown",
            "priority": "medium",
            "reply": text
        }