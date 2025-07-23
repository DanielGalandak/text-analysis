from PyPDF2 import PdfReader
from utils.split_into_paragraphs import split_into_paragraphs  # nebo dej funkci přímo sem
import pdfplumber

def extract_paragraphs_from_pdf(file_path, max_words=300):
    reader = PdfReader(file_path)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    return split_into_paragraphs(full_text, max_words=max_words)


def extract_full_text_from_pdf(pdf_path):
    """
    Extrahuje celý text z PDF dokumentu.
    
    Args:
        pdf_path (str): Cesta k PDF souboru
        
    Returns:
        str: Plný text dokumentu se zachováním odstavců
    """
    
    full_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    
    return "\n\n".join(full_text)