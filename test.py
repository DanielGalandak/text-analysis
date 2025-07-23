
# text k funkci annotate_paragraph() z utils.gpt_client

from utils.gpt_client import annotate_paragraph

# Ukázkový odstavec – můžeš libovolně změnit
paragraph = """
Celní správa České republiky je bezpečnostní sbor podřízený Ministerstvu financí.
GŘC je správní úřad s celostátní působností. Působí podle zákona č. 185/2004 Sb.
"""

# Identifikátor pro test
paragraph_id = "test_001"

# Zavolání funkce
result = annotate_paragraph(paragraph, paragraph_id=paragraph_id)

# Výpis výsledku
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
