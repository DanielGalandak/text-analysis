# utils/load_sentence_annotations.py

import os
import json

def get_sentences_from_file(base_name, data_dir="data"):
    """
    Načte větnou analýzu ze souboru *base_name*_annotated_sentences.json,
    pokud existuje. Jinak vrátí None.
    """
    filename = base_name + "_annotated_sentences.json"
    path = os.path.join(data_dir, filename)

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Soubor {filename} neobsahuje pole bloků vět.")

    return data
