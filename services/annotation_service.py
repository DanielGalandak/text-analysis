from repositories.load_prompt import load_prompt
from utils.analysis_metadata import generate_runtime_metadata
from utils.gpt_client import annotate_paragraph
from models import Annotation, db  # nově

import time
from datetime import datetime

def annotate_paragraph_with_metadata(
    paragraph_text,
    prompt_name,
    paragraph_id="auto_001",
    model="gpt-4o",
    temperature=0.3,
    source_filename=None,
    page=None,
    offset_start=None,
    offset_end=None,
    save_to_db=False
):
    prompt_template = load_prompt(prompt_name)
    prompt_version = prompt_name.replace(".txt", "")
    start_time = time.time()

    result = annotate_paragraph(
        paragraph_text=paragraph_text,
        prompt_template=prompt_template,
        paragraph_id=paragraph_id
    )

    if "error" in result:
        return result

    runtime_info = generate_runtime_metadata(
        start_time=start_time,
        prompt_version=prompt_version,
        model=model,
    )

    result["prompt_version"] = prompt_version
    result["runtime"] = runtime_info

    if save_to_db:
        annotation = Annotation(
            paragraph_id=paragraph_id,
            source_filename=source_filename,
            page=page,
            offset_start=offset_start,
            offset_end=offset_end,
            created_at=datetime.utcnow(),
            model=model,
            prompt_version=prompt_version,
            annotation_data=result
        )
        db.session.add(annotation)
        db.session.commit()

    return result
