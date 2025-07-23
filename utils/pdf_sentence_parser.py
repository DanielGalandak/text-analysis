# utils/pdf_sentence_parser.py

import re
from PyPDF2 import PdfReader

def regex_sentence_tokenize(text):
    """
    Rozdělí text na věty bez použití lookbehind – optimalizováno pro češtinu.
    Chrání běžné zkratky před chybným dělením.
    """
    # Zkratky, za kterými NEchceme dělit
    protected_abbrevs = r"(str|č|např|tj|tzv|atd|resp|cca|srov|čj|mj|příl|apod|čís|obr)"

    # Předrozdělení: nahradíme tečky za zkratkami dočasným tokenem
    placeholder = "<<<DOT>>>"
    text = re.sub(rf"\b{protected_abbrevs}\.", lambda m: m.group(0).replace(".", placeholder), text)

    # Rozdělení vět podle běžných konců (tečka, otazník, vykřičník, trojtečka), následovaných velkým písmenem
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])", text)

    # Obnovení skutečných teček ve zkratkách
    sentences = [s.replace(placeholder, ".").strip() for s in parts if s.strip()]
    return sentences


def extract_sentences_from_pdf(file_path):
    """
    Načte PDF, rozdělí ho na významové věty nebo výčtové celky.
    Výčty zůstávají pohromadě jako "věty".
    """
    reader = PdfReader(file_path)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    sentences = []
    buffer = ""

    for line in lines:
        if re.match(r"^(\-|\•|\d+[.)])", line):
            if buffer:
                sentences.extend(regex_sentence_tokenize(buffer.strip()))
                buffer = ""
            sentences.append(line)
        else:
            buffer += " " + line
            if re.search(r"[.!?…]\s*$", line):
                sentences.extend(regex_sentence_tokenize(buffer.strip()))
                buffer = ""

    if buffer:
        sentences.extend(regex_sentence_tokenize(buffer.strip()))

    return [s.strip() for s in sentences if s.strip()]
