import json
import sys
import os

from utils.analyze_by_sentence import analyze_pdf_by_sentences

def main():
    if len(sys.argv) < 2:
        print("Použití: python test_analyze_by_sentences.py <soubor.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Soubor {pdf_path} neexistuje.")
        sys.exit(1)

    print(f"Analyzuji: {pdf_path}")
    results = analyze_pdf_by_sentences(pdf_path)

    print("\n📊 Výsledky anotace:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Věta {i} ---")
        print("Text:", result["sentence"])
        print("Anotace:", json.dumps(result["annotation"], ensure_ascii=False, indent=2))

    # Volitelně: uložit výstup do JSON
    output_path = os.path.splitext(pdf_path)[0] + "_annotated_sentences.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Výstup uložen do: {output_path}")

if __name__ == "__main__":
    main()
