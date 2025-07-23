# repositiories/load_prompt.py
import os

def load_prompt(prompt_name, base_dir="prompts"):
    path = os.path.join(base_dir, prompt_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
