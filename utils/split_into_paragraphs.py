# utils/split_into_paragraphs.py

def split_into_paragraphs(text, max_words=300):
    """
    Rozdělí text na přirozené chunk-odstavce max do X slov.
    Kombinuje řádky, ale ohraničuje podle délky.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    paragraphs = []
    current_chunk = ""

    for line in lines:
        if not current_chunk:
            current_chunk = line
        elif len((current_chunk + " " + line).split()) <= max_words:
            current_chunk += " " + line
        else:
            paragraphs.append(current_chunk.strip())
            current_chunk = line

    if current_chunk:
        paragraphs.append(current_chunk.strip())

    return paragraphs
