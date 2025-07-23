# utils/naming.py

import os

def name_json_file(upload_filename, output_dir="data/auto"):
    """
    Vygeneruje název JSON souboru ze jména nahraného PDF.
    Pokud soubor už existuje, přidá číslování (_1, _2, ...).
    """
    basename = os.path.splitext(upload_filename)[0]
    filename = f"{basename}.json"
    filepath = os.path.join(output_dir, filename)

    counter = 1
    while os.path.exists(filepath):
        filename = f"{basename}_{counter}.json"
        filepath = os.path.join(output_dir, filename)
        counter += 1

    return filepath
