# services/gpt_chunking_from_sentences.py

from utils.gpt_client import client
from repositories.load_prompt import load_prompt
import json

MAX_SENTENCES_PER_BATCH = 20  # bezpečný limit pro GPT-4o, klidně později doladíme

def group_sentences_into_chunks(sentence_blocks, prompt_name="2025_04_23_chunking_prompt.txt"):
    """
    Rozdělí věty na dávky a posílá je postupně do GPT.
    """
    prompt_template = load_prompt(prompt_name)

    # Připravíme všechny věty
    all_sentences = []
    for block in sentence_blocks:
        for s in block["sentences"]:
            all_sentences.append({
                "id": s["id"],
                "annotation": s["annotation"]
            })

    total_sentences = len(all_sentences)
    print(f"📄 Celkem vět k chunkování: {total_sentences}")

    chunks = []
    batch_number = 0

    # Rozdělíme věty na dávky
    for i in range(0, total_sentences, MAX_SENTENCES_PER_BATCH):
        batch_sentences = all_sentences[i:i+MAX_SENTENCES_PER_BATCH]
        batch_number += 1
        print(f"✉️ Odesílám batch {batch_number}: {len(batch_sentences)} vět")

        # Připravíme prompt pro tuto batch
        prompt = prompt_template.format(sentences=json.dumps(batch_sentences, ensure_ascii=False, indent=2))

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jsi specialista na výroční zprávy. Odpovídej pouze čistým JSONem podle specifikace."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(content)

            if isinstance(result, dict) and "chunks" in result:
                chunks.extend(result["chunks"])
            elif isinstance(result, list):
                chunks.extend(result)  # přímo extendujeme list chunků
            else:
                raise ValueError("⚠️ Neočekávaný formát odpovědi od GPT.")

            print(f"✅ Batch {batch_number} zpracován.")

        except Exception as e:
            print(f"❌ Chyba při zpracování batch {batch_number}: {str(e)}")
            print(f"⚠️ Obdržený obsah:\n{content}")
            raise e

    print(f"✅ Celkem vytvořeno {len(chunks)} tematických chunků.")
    return chunks    

def assemble_paragraphs_from_chunks(sentence_annotations, chunk_structure):
    """
    Vytvoří seznam paragraphů {paragraph_id, text} na základě původních anotací vět a struktury chunků.

    :param sentence_annotations: list původních větných bloků (z annotated_sentences.json)
    :param chunk_structure: list chunků od GPT (chunk_id + sentence_ids)
    :return: list paragraphů {paragraph_id, text}
    """
    # 1. Mapa ID -> text věty
    id_to_sentence = {s["id"]: s["text"] for block in sentence_annotations for s in block["sentences"]}

    # 2. Stavíme seznam paragraphů
    paragraphs = []
    for chunk in chunk_structure:
        paragraph_id = chunk["chunk_id"]
        sentence_texts = [id_to_sentence[sid] for sid in chunk["sentence_ids"] if sid in id_to_sentence]
        paragraph_text = " ".join(sentence_texts)
        paragraphs.append({
            "paragraph_id": paragraph_id,
            "text": paragraph_text
        })

    return paragraphs

