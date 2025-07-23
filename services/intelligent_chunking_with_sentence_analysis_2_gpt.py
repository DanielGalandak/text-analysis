import json
import time
from datetime import datetime
from utils.gpt_client import client
from repositories.load_prompt import load_prompt
from models import Annotation, db


def get_sentences_in_range(sentence_annotations, start_offset, end_offset):
    """Vrátí seznam anotovaných vět, které spadají do zadaného rozsahu."""
    return [
        s for s in sentence_annotations
        if s.get("start_offset") is not None and s.get("end_offset") is not None
        and s["start_offset"] >= start_offset and s["end_offset"] <= end_offset
    ]


def intelligent_chunking_with_sentence_analysis(sentence_annotations, source_filename, prompt_name="chunking_with_context_prompt.txt"):
    """
    Rozdělí větší bloky textu na menší tematické chunky s využitím anotací vět jako kontextu.
    """
    prompt_template = load_prompt(prompt_name)

    # Sestavit velké bloky (např. po 2000 znacích)
    all_text = " ".join(s["text"] for s in sentence_annotations)
    big_chunks = []
    current_text = ""
    current_start = sentence_annotations[0]["start_offset"]
    last_offset = current_start

    for s in sentence_annotations:
        if len(current_text) + len(s["text"]) < 2000:
            current_text += " " + s["text"]
            last_offset = s["end_offset"]
        else:
            big_chunks.append({
                "text": current_text.strip(),
                "start_offset": current_start,
                "end_offset": last_offset
            })
            current_text = s["text"]
            current_start = s["start_offset"]
            last_offset = s["end_offset"]

    if current_text:
        big_chunks.append({
            "text": current_text.strip(),
            "start_offset": current_start,
            "end_offset": last_offset
        })

    results = []
    chunk_counter = 1

    for i, big_chunk in enumerate(big_chunks):
        print(f"📦 Zpracovávám velký chunk {i+1}/{len(big_chunks)}")
        context_sentences = get_sentences_in_range(
            sentence_annotations,
            big_chunk["start_offset"],
            big_chunk["end_offset"]
        )

        prompt = prompt_template.format(
            chunk_text=big_chunk["text"],
            context_sentences=json.dumps([
                {
                    "text": s["text"],
                    "annotation": s.get("annotation", {})
                } for s in context_sentences
            ], ensure_ascii=False, indent=2)
        )

        start_time = time.time()

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Jsi expert na segmentaci dokumentů podle významu."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()

            gpt_chunks = json.loads(content)

            for chunk in gpt_chunks:
                paragraph_id = f"chunk_{chunk_counter}"
                chunk_counter += 1

                chunk["paragraph_id"] = paragraph_id
                chunk["absolute_start"] = big_chunk["start_offset"] + chunk.get("relative_start", 0)
                chunk["absolute_end"] = big_chunk["start_offset"] + chunk.get("relative_end", len(chunk["text"]))

                annotation = Annotation(
                    paragraph_id=paragraph_id,
                    source_filename=source_filename,
                    offset_start=chunk["absolute_start"],
                    offset_end=chunk["absolute_end"],
                    created_at=datetime.utcnow(),
                    model="gpt-4o",
                    prompt_version=prompt_name.replace(".txt", ""),
                    annotation_data={
                        "text": chunk["text"],
                        "chunk_type": chunk.get("chunk_type", "unknown"),
                        "runtime": {
                            "processing_time": time.time() - start_time,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                )
                db.session.add(annotation)
                results.append(chunk)
            db.session.commit()

        except Exception as e:
            print(f"❌ Chyba u chunku {i+1}: {str(e)}")
            db.session.rollback()

    return results
