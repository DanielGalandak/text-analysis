# utils/analysis_metadata.py

import uuid
import time
from datetime import datetime

def generate_runtime_metadata(model="gpt-4o", prompt_version="v1.3", temperature=0.3, start_time=None):
    end_time = time.time()
    duration_ms = int((end_time - start_time) * 1000) if start_time else None

    return {
        "model": model,
        "model_version": "2024-04-18",
        "prompt_version": prompt_version,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "temperature": temperature,
        "token_count_input": None,
        "token_count_output": None,
        "duration_ms": duration_ms,
        "cached_result": False,
        "api_response_id": str(uuid.uuid4())
    }
