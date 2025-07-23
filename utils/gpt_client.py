# gpt_client.py

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

REQUIRED_KEYS = {
    "categories",
    "keywords",
    "type_of_statement",
    "entities",
    "temporal_reference",
    "tone",
    "confidence",
}

def annotate_paragraph(paragraph_text, prompt_template, paragraph_id="auto_001"):
    prompt = prompt_template.format(paragraph_text=paragraph_text)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jsi specialista na analýzu výročních zpráv. Vždy vracej validní JSON podle přesné struktury."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        result = json.loads(content)

        if not REQUIRED_KEYS.issubset(result.keys()):
            return {"error": "Missing required keys", "raw": content}

        result["paragraph_id"] = paragraph_id
        result["text"] = paragraph_text
        return result

    except json.JSONDecodeError:
        return {"error": "Invalid JSON from model", "raw": content}
