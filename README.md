Flask aplikace pro analýzu PDF dokumentů pomocí LLM
Přehled
Tento projekt je webová aplikace postavená na Flasku, která umožňuje:
•	Analýzu PDF dokumentů po odstavcích nebo po větách.
•	Inteligentní seskupování vět do tematických bloků (chunků) s využitím LLM (GPT).
•	Automatickou anotaci textu pomocí připravených promptů.
•	Správu a zobrazení uložených anotací ve formátu JSON a databázi (SQLite).
Aplikace umožňuje uživateli nahrát PDF, zvolit režim analýzy a prohlížet výsledné anotace.
________________________________________
Hlavní funkce
•	Nahrávání PDF souborů přes /upload.
•	Analýza textu:
o	Režim sentence – analýza po větách (analyze_pdf_by_sentences).
o	Režim chunk – rozdělení na bloky (chunky) pro následnou anotaci.
o	Režim ai_from_sentence – seskupení vět pomocí LLM do tematických chunků.
•	Automatická anotace textu s použitím promptů (annotation_service).
•	Správa JSON výstupů (uložené soubory v data/).
•	Ukládání anotací do databáze SQLite (model Annotation).
________________________________________
Struktura projektu
bash
ZkopírovatUpravit
app.py                     	# Hlavní Flask aplikace
models.py                  	# SQLAlchemy modely (Annotation)
test.py                    	# Základní testy
test_analyze_by_sentences.py
data/                      	# Výstupy analýz (JSON)
uploads/                   	# Nahraná PDF
prompts/                  	# Soubory promptů pro LLM
repositories/load_prompt.py
services/                  	# Logika (anotace, chunking, GPT)
templates/                 	# HTML šablony
uml/                       	# UML diagramy
utils/                     	# PDF parsery, analýzy, nástroje
instance/                  	# Databáze SQLite
________________________________________
Instalace a spuštění
1.	Naklonujte repozitář:
bash
ZkopírovatUpravit
git clone <repo-url>
cd <repo-directory>
2.	Vytvořte a aktivujte virtuální prostředí:
bash
ZkopírovatUpravit
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
3.	Nainstalujte závislosti:
bash
ZkopírovatUpravit
pip install -r requirements.txt
4.	Inicializujte databázi a spusťte server:
bash
ZkopírovatUpravit
python app.py
Aplikace poběží na http://127.0.0.1:5000/.
________________________________________
Technologie
•	Python 3.10+
•	Flask (webový framework)
•	SQLAlchemy (ORM pro SQLite databázi)
•	OpenAI/LLM API (pro chunking a anotace)
•	PDF parsování (pdf_parser, pdf_sentence_parser)
•	HTML/CSS šablony pro uživatelské rozhraní

