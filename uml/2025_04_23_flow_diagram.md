# UML Activity diagram aplikace pro analýzu výročních zpráv

```mermaid
stateDiagram-v2
    [*] --> NahrátPDF: Uživatel nahraje PDF
    NahrátPDF --> VýběrRežimu
    
    state VýběrRežimu <<choice>>
    VýběrRežimu --> ExtrakceOdstavců: chunk režim
    VýběrRežimu --> ExtrakceVět: sentence režim
    
    ExtrakceOdstavců --> CyklusPřesOdstavce: extract_paragraphs_from_pdf
    CyklusPřesOdstavce --> AnotaceOdstavce: Pro každý odstavec
    
    ExtrakceVět --> CyklusPřesVěty: extract_sentences_from_pdf
    CyklusPřesVěty --> AnotaceVěty: Pro každou větu
    AnotaceVěty --> SeskupeníVět: Seskupení do chunků
    
    state AnotačníProces {
        [*] --> NačteníPromptu: load_prompt
        NačteníPromptu --> VoláníGPT: annotate_paragraph
        VoláníGPT --> KontrolaJSON: Validace výstupu
        KontrolaJSON --> PřidáníMetadat: generate_runtime_metadata
        PřidáníMetadat --> UloženíDoDB: Volitelné
    }
    
    AnotaceOdstavce --> AnotačníProces
    AnotaceVěty --> AnotačníProces
    
    AnotačníProces --> UloženíVýsledků
    SeskupeníVět --> UloženíVýsledků
    
    UloženíVýsledků --> ZobrazeníVUI
    ZobrazeníVUI --> [*]
