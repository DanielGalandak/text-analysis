from utils.pdf_sentence_parser import extract_sentences_from_pdf
from services.annotation_service import annotate_paragraph_with_metadata

def analyze_pdf_by_sentences(file_path, chunk_size=5):
    sentences = extract_sentences_from_pdf(file_path)
    results = []

    chunk = []
    prompt_name = "2025_04_22_prompt_2.txt"  # můžeš přizpůsobit pro větný režim

    for i, sentence in enumerate(sentences):
        print(f"🔄 Věta {i+1}/{len(sentences)}")
        paragraph_id = f"sent_{i+1}"

        annotated = annotate_paragraph_with_metadata(
            paragraph_text=sentence,
            prompt_name=prompt_name,
            paragraph_id=paragraph_id
        )

        chunk.append({
            "id": paragraph_id,
            "text": sentence,
            "annotation": annotated
        })

        if len(chunk) == chunk_size or i == len(sentences) - 1:
            combined_text = " ".join(s["text"] for s in chunk)
            chunk_id = f"chunk_{len(results)+1}"
            results.append({
                "paragraph_id": chunk_id,
                "text": combined_text,
                "sentences": chunk
            })
            chunk = []
            print(f"📦 Vytvořen blok {chunk_id} s {len(chunk)} větami")

    return results
