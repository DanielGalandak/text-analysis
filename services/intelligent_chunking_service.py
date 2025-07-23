# services/intelligent_chunking_service.py

from utils.gpt_client import client
from repositories.load_prompt import load_prompt
import json
from models import Annotation, db
from datetime import datetime
import time

def intelligent_chunking_from_raw_text(full_text, source_filename, chunk_size=3000, overlap=500, 
                                       prompt_name="chunk_boundary_detection_prompt.txt"):
    """
    Rozdělí celý text na chunky podle přirozených hranic odstavců s pomocí jazykového modelu.
    
    1. Postupně posílá překrývající se části textu modelu
    2. Pro každou část model identifikuje začátky a konce odstavců
    3. Výsledky se průběžně ukládají
    
    Args:
        full_text (str): Celý text dokumentu
        source_filename (str): Název zdrojového souboru
        chunk_size (int): Maximální velikost části textu zasílaná modelu
        overlap (int): Překryv mezi částmi textu (aby se nerozdělily odstavce)
        prompt_name (str): Název souboru s promptem
    
    Returns:
        list: Seznam identifikovaných logických chunků, každý s metadaty
    """
    prompt_template = load_prompt(prompt_name)
    
    # Rozdělit text na překrývající se části
    raw_chunks = []
    start = 0
    while start < len(full_text):
        end = min(start + chunk_size, len(full_text))
        # Pokud nejsme na konci, najít lepší místo pro rozdělení (např. konec odstavce)
        if end < len(full_text):
            # Hledáme konec odstavce v překryvu
            possible_end = full_text.rfind('\n\n', start + chunk_size - overlap, end)
            if possible_end > 0:
                end = possible_end
        
        raw_chunks.append({
            "text": full_text[start:end],
            "start_position": start,
            "end_position": end
        })
        
        # Posunout začátek další části, přeskočit překryv
        if end == len(full_text):
            break
        start = end - overlap
    
    print(f"Text rozdělen na {len(raw_chunks)} překrývajících se částí pro zpracování")
    
    # Zpracovat každou část a identifikovat logické celky
    logical_chunks = []
    chunk_counter = 1
    
    for i, raw_chunk in enumerate(raw_chunks):
        print(f"Zpracovávám část {i+1}/{len(raw_chunks)}...")
        
        prompt = prompt_template.format(
            text=raw_chunk["text"],
            start_position=raw_chunk["start_position"],
            end_position=raw_chunk["end_position"]
        )
        
        start_time = time.time()
        
        # Požádat model o identifikaci logických celků
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jsi specialista na analýzu dokumentů. Identifikuješ přirozené hranice odstavců a logických celků. Výstup musí být validní JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        try:
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
                
            detected_chunks = json.loads(content)
            
            # Zpracování a uložení identifikovaných chunků
            for chunk_data in detected_chunks:
                # Ověřit, zda chunk obsahuje všechny potřebné informace
                if "text" not in chunk_data or not chunk_data["text"].strip():
                    continue
                    
                # Přidat metadata
                chunk_id = f"chunk_{chunk_counter}"
                chunk_counter += 1
                
                chunk_data["paragraph_id"] = chunk_id
                chunk_data["absolute_start"] = raw_chunk["start_position"] + chunk_data.get("relative_start", 0)
                chunk_data["absolute_end"] = raw_chunk["start_position"] + chunk_data.get("relative_end", len(chunk_data["text"]))
                
                # Uložit do DB, pokud je potřeba
                annotation = Annotation(
                    paragraph_id=chunk_id,
                    source_filename=source_filename,
                    offset_start=chunk_data["absolute_start"],
                    offset_end=chunk_data["absolute_end"],
                    created_at=datetime.utcnow(),
                    model="gpt-4o",  # nebo parametr
                    prompt_version=prompt_name.replace(".txt", ""),
                    annotation_data={
                        "text": chunk_data["text"],
                        "chunk_type": chunk_data.get("chunk_type", "unknown"),
                        "runtime": {
                            "processing_time": time.time() - start_time,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                )
                db.session.add(annotation)
                logical_chunks.append(chunk_data)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Chyba při zpracování části {i+1}: {str(e)}")
            db.session.rollback()
            # Uložit alespoň nezpracovaný text pro budoucí zpracování
            chunk_id = f"error_chunk_{chunk_counter}"
            chunk_counter += 1
            
            annotation = Annotation(
                paragraph_id=chunk_id,
                source_filename=source_filename,
                offset_start=raw_chunk["start_position"],
                offset_end=raw_chunk["end_position"],
                created_at=datetime.utcnow(),
                model="gpt-4o",
                prompt_version=prompt_name.replace(".txt", ""),
                annotation_data={
                    "text": raw_chunk["text"],
                    "error": str(e),
                    "status": "error",
                    "runtime": {
                        "processing_time": time.time() - start_time,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
            db.session.add(annotation)
            db.session.commit()
    
    # Odstranit duplicity z překrývajících se částí
    deduplicated_chunks = deduplicate_chunks(logical_chunks)
    print(f"Identifikováno {len(deduplicated_chunks)} logických celků")
    
    return deduplicated_chunks

def deduplicate_chunks(chunks):
    """
    Odstraní překrývající se chunky na základě absolutních pozic
    """
    # Seřadit podle absolutní pozice začátku
    sorted_chunks = sorted(chunks, key=lambda x: x.get("absolute_start", 0))
    
    result = []
    last_end = -1
    
    for chunk in sorted_chunks:
        start = chunk.get("absolute_start", 0)
        
        # Pokud je začátek tohoto chunku před koncem předchozího, máme překryv
        if start <= last_end:
            # Je překryv dostatečně malý na to, abychom ho mohli ignorovat?
            if start > last_end - 50:  # tolerujeme malý překryv (např. 50 znaků)
                result.append(chunk)
                last_end = chunk.get("absolute_end", start + len(chunk.get("text", "")))
            else:
                # Jinak tento chunk přeskočíme (je duplikát)
                print(f"Přeskakuji duplikátní chunk: {chunk['paragraph_id']}")
        else:
            # Žádný překryv, přidáme do výsledku
            result.append(chunk)
            last_end = chunk.get("absolute_end", start + len(chunk.get("text", "")))
    
    return result