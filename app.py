from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import json

from utils.pdf_parser import extract_paragraphs_from_pdf
from utils.analyze_by_sentence import analyze_pdf_by_sentences
from utils.load_sentence_annotations import get_sentences_from_file

from services.gpt_chunking_from_sentences import group_sentences_into_chunks, assemble_paragraphs_from_chunks
from services.annotation_service import annotate_paragraph_with_metadata
from services.intelligent_chunking_with_sentence_analysis_2_gpt import intelligent_chunking_with_sentence_analysis


from models import db, Annotation

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "annotations.db")
db.init_app(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DATA_FOLDER"] = DATA_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        pdf_file = request.files["pdf_file"]
        mode = request.form.get("mode", "chunk")  # "chunk" or "sentence"

        if pdf_file.filename == "":
            return "Nebyl vybrán žádný soubor."

        # Uložení nahraného PDF
        filename = secure_filename(pdf_file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(upload_path)

        # Základ názvu výstupního JSON
        base_name = os.path.splitext(filename)[0]

        if mode == "sentence":
            print("🔍 Spouští se analýza po větách...")
            result = analyze_pdf_by_sentences(upload_path)
            json_name = base_name + "_annotated_sentences.json"
        
        elif mode == "ai_from_sentence":
            sentence_annotations = get_sentences_from_file(base_name, app.config['DATA_FOLDER'])
            if sentence_annotations is None:
                return "❌ Chybí soubor s větnou analýzou. Spusťte nejprve analýzu vět nebo nahrajte JSON ručně."

            print("🤖 Seskupování vět do tématických bloků (GPT)...")

            chunks = group_sentences_into_chunks(sentence_annotations)       
            # paragraphs = assemble_paragraphs_from_chunks(sentence_annotations, chunks)

            paragraphs = []
            for chunk in chunks:
                paragraphs.append({
                    "paragraph_id": chunk["paragraph_id"],
                    "text": chunk["text"]
                })

            result = []
            total = len(paragraphs)

            prompt_name = "2025_04_22_prompt_2.txt"

            for i, p in enumerate(paragraphs):
                print(f"🔄 Chunk {i+1}/{total} ({len(p['text'].split())} slov)")
                paragraph_id = p["paragraph_id"]
                try:
                    annotated = annotate_paragraph_with_metadata(
                        paragraph_text=p["text"],
                        prompt_name=prompt_name,
                        paragraph_id=paragraph_id,
                        source_filename=filename,
                        save_to_db=True
                    )
                except Exception as e:
                    annotated = {
                        "paragraph_id": paragraph_id,
                        "error": str(e),
                        "text": p["text"]
                    }
                result.append(annotated)

            json_name = base_name + "_ai_chunks_annotated.json"
 
        else:
            print("🔍 Spouští se analýza po chuncích...")
            paragraphs = extract_paragraphs_from_pdf(upload_path)
            result = []
            total = len(paragraphs)

            prompt_name = "2025_04_22_prompt_2.txt"  # prozatím natvrdo
            
            for i, p in enumerate(paragraphs):
                print(f"🔄 Chunk {i+1}/{total}")
                paragraph_id = f"chunk_{i+1}"
                try:
                    annotated = annotate_paragraph_with_metadata(
                        paragraph_text=p,
                        prompt_name=prompt_name,
                        paragraph_id=paragraph_id,
                        source_filename=filename,
                        save_to_db=True
                    )
                except Exception as e:
                    annotated = {
                        "paragraph_id": paragraph_id,
                        "error": str(e),
                        "text": p
                    }
                result.append(annotated)

            json_name = base_name + "_annotated.json"

        # Uložení výsledného JSON do složky /data
        output_path = os.path.join(app.config['DATA_FOLDER'], json_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ Výsledek uložen do {output_path}")
        return redirect(url_for("index"))

    return render_template("upload.html")

@app.route("/")
def index():
    data_dir = app.config["DATA_FOLDER"]

    # Získání seznamu všech JSON souborů
    all_files = sorted(
        [f for f in os.listdir(data_dir) if f.endswith(".json")],
        key=lambda x: os.path.getmtime(os.path.join(data_dir, x)),
        reverse=True
    )

    # Sestavíme objekty se jménem a typem
    files = []
    for fname in all_files:
        if "_annotated_sentences" in fname:
            analysis_type = "Věty"
            tag = "🔹"
        elif "_annotated" in fname:
            analysis_type = "Chunky"
            tag = "🔸"
        else:
            analysis_type = "Neznámé"
            tag = "❓"

        files.append({
            "name": fname,
            "type": analysis_type,
            "tag": tag
        })

    selected_filename = request.args.get("file", files[0]["name"] if files else None)
    selected_path = os.path.join(data_dir, selected_filename) if selected_filename else None

    # Načtení obsahu zvoleného JSON
    data = []
    if selected_path and os.path.exists(selected_path):
        with open(selected_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Typ analýzy pro podmíněné vykreslení
    if selected_filename and "_sentences" in selected_filename:
        selected_analysis = "sentence"
    else:
        selected_analysis = "chunk"

    return render_template(
        "index.html",
        files=files,
        selected_filename=selected_filename,
        paragraphs=data,
        analysis_type=selected_analysis
    )

@app.route("/annotations")
def view_annotations():
    annotations = Annotation.query.order_by(Annotation.created_at.desc()).limit(100).all()

    return render_template("annotations.html", annotations=annotations)

if __name__ == "__main__":
    with app.app_context():
        print("📂 Inicializuji databázi:", app.config["SQLALCHEMY_DATABASE_URI"])
        db.create_all()  # vytvoří tabulku annotation
    app.run(debug=True)

