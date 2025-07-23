```mermaid
stateDiagram-v2
    [*] --> NahrátPDF: Uživatel nahraje PDF
    
    NahrátPDF --> VýběrCesty
    
    state VýběrCesty <<choice>>
    VýběrCesty --> ManualChunking: Chunky (300 slov)
    VýběrCesty --> SentenceAnalysis: Sentence analýza
    VýběrCesty --> AIChunking: Chunky AI (přímo)
    
    ManualChunking --> AnotaceOdstavce: Pro každý chunk
    SentenceAnalysis --> AnotaceVěty: Pro každou větu
    AnotaceVěty --> AIChunking: Seskupení do tematických chunků
    
    AIChunking --> AnotaceChunku: Pro každý AI chunk

    state AnotačníProces {
        [*] --> NačteníPromptu: load_prompt
        NačteníPromptu --> VoláníGPT: annotate_paragraph
        VoláníGPT --> KontrolaJSON: Validace výstupu
        KontrolaJSON --> PřidáníMetadat: generate_runtime_metadata
        PřidáníMetadat --> UloženíDoDB: Volitelné
    }

    AnotaceOdstavce --> AnotačníProces
    AnotaceVěty --> AnotačníProces
    AnotaceChunku --> AnotačníProces

    AnotačníProces --> UloženíVýsledků
    AIChunking --> UloženíVýsledků
    
    UloženíVýsledků --> ZobrazeníVUI
    ZobrazeníVUI --> [*]
```