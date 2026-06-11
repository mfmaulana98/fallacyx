import json
import re

# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_PROMPT_ID = """Kamu adalah ahli logika dan critical thinking yang bertugas mendeteksi cacat logika (logical fallacy) dalam sebuah teks.

IKUTI ATURAN BERIKUT DENGAN SANGAT KETAT:
1. FORMAT OUTPUT: Selalu kembalikan output dalam format JSON yang valid. JANGAN menyertakan teks pengantar, penutup, penjelasan, atau markdown wrapper (seperti ```json ... ```) di luar JSON tersebut. Output harus berupa raw JSON string yang dapat langsung di-parse menggunakan json.loads().
2. TONE: Berikan penjelasan dengan nada yang edukatif, objektif, netral, dan tidak menghakimi (non-judgmental). Penjelasan harus mudah dipahami oleh orang awam.
3. DETEKSI & CONFIDENCE: Hanya tandai pernyataan sebagai fallacy jika tingkat keyakinan (confidence) kamu terhadap keberadaan fallacy tersebut bernilai >= 0.7 (dalam skala 0.0 - 1.0). Jika confidence < 0.7, abaikan pernyataan tersebut. Minimalisasi false positive.
4. KETIDAKADAAN FALLACY: Jika tidak ada fallacy yang terdeteksi dengan confidence >= 0.7, isi properti "fallacies" dengan array kosong ([]) dan jangan kembalikan null atau menghilangkan properti tersebut.
5. BAHASA: Kamu harus mampu menganalisis konten dalam Bahasa Indonesia maupun Bahasa Inggris. Berikan penjelasan dan penilaian keseluruhan dalam bahasa yang disesuaikan dengan parameter atau bahasa input (default: Bahasa Indonesia)."""

SYSTEM_PROMPT_EN = """You are a logician and critical thinking expert tasked with detecting logical fallacies in a given text.

FOLLOW THESE RULES STRICTLY:
1. OUTPUT FORMAT: Always return the output in a valid and strict JSON format. DO NOT include any introductory text, concluding remarks, explanations, or markdown wrappers (like ```json ... ```) outside the JSON. The output must be a raw JSON string that can be directly parsed using json.loads().
2. TONE: Provide explanations in an educational, objective, neutral, and non-judgmental tone. The explanation must be easy to understand for laypeople.
3. DETECTION & CONFIDENCE: Only flag a statement as a fallacy if your confidence score in the presence of that fallacy is >= 0.7 (on a scale of 0.0 to 1.0). If confidence < 0.7, ignore it. Minimize false positives.
4. NO FALLACY: If no fallacy is detected with confidence >= 0.7, set the "fallacies" property to an empty array ([]) and do not return null or omit the property.
5. LANGUAGE: You must be able to analyze content in both Indonesian and English. Provide the explanation and overall assessment in the language requested (default: English)."""

# Default mapping (Indonesian as default)
SYSTEM_PROMPT = SYSTEM_PROMPT_ID


# =============================================================================
# QUICK MODE PROMPT TEMPLATES (DETECTION & VIDEO)
# =============================================================================

DETECTION_PROMPT_TEMPLATE_ID = """Analisis teks berikut untuk mendeteksi logical fallacy:

[Teks untuk Dianalisis]
{text}

[Format Output JSON yang Strict]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Nama Fallacy",
      "text": "kalimat persis yang mengandung fallacy",
      "explanation": "penjelasan singkat 2-3 kalimat mengapa ini fallacy",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": null,
      "timestamp_end": null
    }}
  ],
  "overall_assessment": "1-2 kalimat penilaian keseluruhan tentang kualitas logika argumen",
  "logic_score": 75
}}"""

DETECTION_PROMPT_TEMPLATE_EN = """Analyze the following text to detect logical fallacies:

[Text to Analyze]
{text}

[Strict JSON Output Format]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Fallacy Name",
      "text": "exact sentence containing the fallacy",
      "explanation": "brief 2-3 sentence explanation of why this is a fallacy",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": null,
      "timestamp_end": null
    }}
  ],
  "overall_assessment": "1-2 sentence overall assessment of the logical quality of the argument",
  "logic_score": 75
}}"""

VIDEO_PROMPT_TEMPLATE_ID = """Analisis transkrip video berikut yang dilengkapi dengan timestamp untuk mendeteksi logical fallacy:

[Transkrip Video]
{transcript_with_timestamps}

[Instruksi Tambahan Timestamp]
Konversikan format timestamp [hh:mm:ss] atau [mm:ss] dari kalimat yang mengandung fallacy menjadi jumlah detik (integer). Simpan hasil konversi tersebut ke dalam properti "timestamp_start" and "timestamp_end". Jika fallacy mencakup satu baris, gunakan timestamp baris tersebut sebagai start dan end.

[Format Output JSON yang Strict]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Nama Fallacy",
      "text": "kalimat persis yang mengandung fallacy",
      "explanation": "penjelasan singkat 2-3 kalimat mengapa ini fallacy",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": 83,
      "timestamp_end": 88
    }}
  ],
  "overall_assessment": "1-2 kalimat penilaian keseluruhan tentang kualitas logika argumen",
  "logic_score": 75
}}"""

VIDEO_PROMPT_TEMPLATE_EN = """Analyze the following video transcript with timestamps to detect logical fallacies:

[Video Transcript]
{transcript_with_timestamps}

[Additional Timestamp Instructions]
Convert the timestamp format [hh:mm:ss] or [mm:ss] of the sentence containing the fallacy into total seconds (integer). Save this value in the "timestamp_start" and "timestamp_end" properties. If a fallacy spans a single line, use that line's timestamp as start and end.

[Strict JSON Output Format]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Fallacy Name",
      "text": "exact sentence containing the fallacy",
      "explanation": "brief 2-3 sentence explanation of why this is a fallacy",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": 83,
      "timestamp_end": 88
    }}
  ],
  "overall_assessment": "1-2 sentence overall assessment of the logical quality of the argument",
  "logic_score": 75
}}"""

# Default mappings
DETECTION_PROMPT_TEMPLATE = DETECTION_PROMPT_TEMPLATE_ID
VIDEO_PROMPT_TEMPLATE = VIDEO_PROMPT_TEMPLATE_ID


# =============================================================================
# EDUCATIONAL MODE PROMPT TEMPLATES (TEXT & VIDEO)
# =============================================================================

EDUCATIONAL_PROMPT_TEMPLATE_ID = """Analisis teks berikut secara mendalam untuk mode belajar (edukatif):

[Teks untuk Dianalisis]
{text}

[Format Output JSON yang Strict - Mode Belajar]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Nama Fallacy",
      "text": "kalimat persis yang mengandung fallacy",
      "explanation": "Penjelasan detail 3-4 kalimat mengapa kalimat ini merupakan fallacy.",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": null,
      "timestamp_end": null,
      "detailed_explanation": "Penjelasan mendalam mengenai konsep logika di balik fallacy ini secara akademis namun mudah dipahami.",
      "similar_examples": [
        "Contoh lain 1 yang mirip dengan fallacy ini beserta penjelasan singkatnya.",
        "Contoh lain 2 yang mirip dengan fallacy ini beserta penjelasan singkatnya."
      ],
      "how_to_avoid": "Cara konkret dan taktis untuk menghindari kesalahan logika serupa di masa depan."
    }}
  ],
  "overall_assessment": "Penilaian keseluruhan yang komprehensif mengenai struktur logika dari argumen yang dianalisis.",
  "logic_score": 75
}}"""

EDUCATIONAL_PROMPT_TEMPLATE_EN = """Analyze the following text in depth for learning mode (educational):

[Text to Analyze]
{text}

[Strict JSON Output Format - Learning Mode]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Fallacy Name",
      "text": "exact sentence containing the fallacy",
      "explanation": "Detailed 3-4 sentence explanation of why this sentence is a fallacy.",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": null,
      "timestamp_end": null,
      "detailed_explanation": "In-depth academic yet accessible explanation of the logical concept behind this fallacy.",
      "similar_examples": [
        "Another similar example of this fallacy with a brief explanation.",
        "Another similar example of this fallacy with a brief explanation."
      ],
      "how_to_avoid": "Concrete and tactical ways to avoid similar logical errors in the future."
    }}
  ],
  "overall_assessment": "A comprehensive overall assessment of the logical structure of the analyzed argument.",
  "logic_score": 75
}}"""

EDUCATIONAL_VIDEO_PROMPT_TEMPLATE_ID = """Analisis transkrip video berikut yang dilengkapi dengan timestamp secara mendalam untuk mode belajar (edukatif):

[Transkrip Video]
{transcript_with_timestamps}

[Instruksi Tambahan Timestamp]
Konversikan format timestamp [hh:mm:ss] atau [mm:ss] dari kalimat yang mengandung fallacy menjadi jumlah detik (integer). Simpan hasil konversi tersebut ke dalam properti "timestamp_start" dan "timestamp_end". Jika fallacy mencakup satu baris, gunakan timestamp baris tersebut sebagai start dan end.

[Format Output JSON yang Strict - Mode Belajar dengan Timestamp]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Nama Fallacy",
      "text": "kalimat persis yang mengandung fallacy",
      "explanation": "Penjelasan detail 3-4 kalimat mengapa kalimat ini merupakan fallacy.",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": 83,
      "timestamp_end": 88,
      "detailed_explanation": "Penjelasan mendalam mengenai konsep logika di balik fallacy ini secara akademis namun mudah dipahami.",
      "similar_examples": [
        "Contoh lain 1 yang mirip dengan fallacy ini beserta penjelasan singkatnya.",
        "Contoh lain 2 yang mirip dengan fallacy ini beserta penjelasan singkatnya."
      ],
      "how_to_avoid": "Cara konkret dan taktis untuk menghindari kesalahan logika serupa di masa depan."
    }}
  ],
  "overall_assessment": "Penilaian keseluruhan yang komprehensif mengenai struktur logika dari argumen yang dianalisis.",
  "logic_score": 75
}}"""

EDUCATIONAL_VIDEO_PROMPT_TEMPLATE_EN = """Analyze the following video transcript with timestamps in depth for learning mode (educational):

[Video Transcript]
{transcript_with_timestamps}

[Additional Timestamp Instructions]
Convert the timestamp format [hh:mm:ss] or [mm:ss] of the sentence containing the fallacy into total seconds (integer). Save this value in the "timestamp_start" and "timestamp_end" properties. If a fallacy spans a single line, use that line's timestamp as start and end.

[Strict JSON Output Format - Learning Mode with Timestamp]
{{
  "fallacies": [
    {{
      "type": "snake_case_fallacy_name",
      "type_label": "Fallacy Name",
      "text": "exact sentence containing the fallacy",
      "explanation": "Detailed 3-4 sentence explanation of why this sentence is a fallacy.",
      "confidence": 0.95,
      "severity": "high|medium|low",
      "timestamp_start": 83,
      "timestamp_end": 88,
      "detailed_explanation": "In-depth academic yet accessible explanation of the logical concept behind this fallacy.",
      "similar_examples": [
        "Another similar example of this fallacy with a brief explanation.",
        "Another similar example of this fallacy with a brief explanation."
      ],
      "how_to_avoid": "Concrete and tactical ways to avoid similar logical errors in the future."
    }}
  ],
  "overall_assessment": "A comprehensive overall assessment of the logical structure of the analyzed argument.",
  "logic_score": 75
}}"""

# Default mapping
EDUCATIONAL_PROMPT_TEMPLATE = EDUCATIONAL_PROMPT_TEMPLATE_ID


# =============================================================================
# FEW-SHOT EXAMPLES (INDONESIAN & ENGLISH)
# =============================================================================

FEW_SHOT_EXAMPLES = [
    {
        "input": "Kita tidak perlu mendengarkan pendapat dia tentang kebijakan ekonomi baru ini, karena dia sendiri kan pernah gagal mengelola bisnisnya sendiri dan orangnya sangat emosional.",
        "output": {
            "fallacies": [
                {
                    "type": "ad_hominem",
                    "type_label": "Ad Hominem",
                    "text": "Kita tidak perlu mendengarkan pendapat dia tentang kebijakan ekonomi baru ini, karena dia sendiri kan pernah gagal mengelola bisnisnya sendiri dan orangnya sangat emosional.",
                    "explanation": "Argumen ini menyerang kegagalan pribadi pembicara di masa lalu dan sifat emosionalnya daripada membahas substansi argumen ekonominya. Karakter atau masa lalu seseorang tidak secara otomatis membuat argumen ekonominya salah.",
                    "confidence": 0.95,
                    "severity": "medium",
                    "timestamp_start": None,
                    "timestamp_end": None,
                    "detailed_explanation": "Ad Hominem terjadi ketika argumen diarahkan untuk menyerang kepribadian, karakter, latar belakang, atau atribut pribadi lawan bicara alih-alih menyanggah substansi argumen yang diajukan. Secara formal, kredibilitas pribadi pembicara tidak menentukan validitas logis dari premis yang mereka buat.",
                    "similar_examples": [
                        "Jangan percaya sarannya tentang nutrisi karena dia kelebihan berat badan.",
                        "Tentu saja dia mendukung kenaikan pajak, dia kan anggota partai sosialis."
                    ],
                    "how_to_avoid": "Tetap fokus pada kekuatan pembuktian, kebenaran premis, dan validitas inferensi dari argumen lawan, bukan pada kepribadian atau masa lalu mereka."
                }
            ],
            "overall_assessment": "Pernyataan ini menolak argumen lawan bicara secara tidak sah dengan menyerang pribadi pembicara, bukan isi argumennya.",
            "logic_score": 60
        }
    },
    {
        "input": "Kalau kita menyetujui anggaran untuk program lingkungan ini, berarti kita membiarkan sektor pendidikan kelaparan tanpa dana. Kita harus memilih: peduli pada alam atau peduli pada masa depan anak-anak kita. Kelompok pencinta lingkungan ingin kita kembali hidup di zaman purba tanpa teknologi.",
        "output": {
            "fallacies": [
                {
                    "type": "false_dilemma",
                    "type_label": "False Dilemma (Dilema Palsu)",
                    "text": "Kalau kita menyetujui anggaran untuk program lingkungan ini, berarti kita membiarkan sektor pendidikan kelaparan tanpa dana. Kita harus memilih: peduli pada alam atau peduli pada masa depan anak-anak kita.",
                    "explanation": "Argumen ini menyajikan dua pilihan ekstrem seolah-olah tidak ada opsi kompromi, padahal anggaran bisa dialokasikan secara seimbang untuk program lingkungan maupun pendidikan.",
                    "confidence": 0.96,
                    "severity": "high",
                    "timestamp_start": None,
                    "timestamp_end": None,
                    "detailed_explanation": "False Dilemma (atau bifurcation) terjadi ketika argumen membatasi pilihan yang tersedia menjadi dua opsi ekstrem saja, padahal terdapat pilihan-pilihan moderat atau solusi lain di antaranya. Ini sering digunakan untuk memaksa audiens memilih satu opsi yang diinginkan pembuat argumen.",
                    "similar_examples": [
                        "Jika kamu tidak mendukung perang ini, berarti kamu adalah musuh negara.",
                        "Kamu ingin melanjutkan kuliah atau menjadi pengangguran seumur hidup?"
                    ],
                    "how_to_avoid": "Selalu cari alternatif ketiga atau opsi tengah. Sadarilah bahwa alokasi sumber daya atau pilihan kebijakan jarang sekali bersifat mutlak biner."
                },
                {
                    "type": "strawman",
                    "type_label": "Strawman (Manusia Jerami)",
                    "text": "Kelompok pencinta lingkungan ingin kita kembali hidup di zaman purba tanpa teknologi.",
                    "explanation": "Pernyataan ini menyalahartikan posisi kelompok pencinta lingkungan dengan melebih-lebihkan menjadi posisi ekstrem yang tidak realistis (hidup di zaman purba) agar lebih mudah diserang.",
                    "confidence": 0.92,
                    "severity": "medium",
                    "timestamp_start": None,
                    "timestamp_end": None,
                    "detailed_explanation": "Strawman fallacy terjadi ketika argumen seseorang diputarbalikkan, disalahartikan, atau disederhanakan secara berlebihan oleh lawan agar terlihat lemah atau konyol, sehingga lebih mudah diserang dan diruntuhkan.",
                    "similar_examples": [
                        "Orang yang ingin membatasi penjualan senjata api sebenarnya ingin menyita semua alat bela diri warga sipil.",
                        "Dia setuju kita perlu membatasi penggunaan gawai pada anak, itu artinya dia ingin anak-anak kita buta teknologi."
                    ],
                    "how_to_avoid": "Gambarkan posisi lawan bicara seakurat dan sejujur mungkin sebelum membantahnya. Jika ragu, tanyakan klarifikasi posisi mereka terlebih dahulu."
                }
            ],
            "overall_assessment": "Argumen ini menggunakan penyederhanaan berlebih dengan menyajikan pilihan biner yang keliru serta menyerang posisi lawan yang sudah diputarbalikkan.",
            "logic_score": 40
        }
    },
    {
        "input": "Olahraga secara teratur selama 30 menit setiap hari dapat membantu menjaga kesehatan jantung dan meningkatkan kebugaran fisik berdasarkan berbagai studi medis.",
        "output": {
            "fallacies": [],
            "overall_assessment": "Argumen ini logis dan didasarkan pada referensi ilmiah medis tanpa adanya cacat logika.",
            "logic_score": 100
        }
    }
]

FEW_SHOT_EXAMPLES_EN = [
    {
        "input": "We shouldn't listen to his opinion on this new economic policy because he failed to manage his own business in the past and he is a very emotional person.",
        "output": {
            "fallacies": [
                {
                    "type": "ad_hominem",
                    "type_label": "Ad Hominem",
                    "text": "We shouldn't listen to his opinion on this new economic policy because he failed to manage his own business in the past and he is a very emotional person.",
                    "explanation": "This argument attacks the speaker's personal past failure and emotional character rather than addressing the substance of his economic argument. A person's character or past does not automatically make their economic argument invalid.",
                    "confidence": 0.95,
                    "severity": "medium",
                    "timestamp_start": None,
                    "timestamp_end": None,
                    "detailed_explanation": "Ad Hominem occurs when an argument is directed at attacking the opponent's personality, character, background, or personal attributes instead of refuting the substance of the argument. Formally, a speaker's personal credibility does not determine the logical validity of their premises.",
                    "similar_examples": [
                        "Do not trust his advice on nutrition because he is overweight.",
                        "Of course he supports tax hikes, he is a member of the socialist party."
                    ],
                    "how_to_avoid": "Focus on the strength of the evidence, the truth of the premises, and the validity of the inferences in the opponent's argument, not on their personality or past."
                }
            ],
            "overall_assessment": "This statement invalidly rejects the opponent's argument by attacking their person instead of the argument itself.",
            "logic_score": 60
        }
    },
    {
        "input": "If we approve the budget for this environmental program, it means we are leaving the education sector to starve without funding. We have to choose: care about nature or care about our children's future. Environmentalists want us to go back to living in prehistoric times without technology.",
        "output": {
            "fallacies": [
                {
                    "type": "false_dilemma",
                    "type_label": "False Dilemma",
                    "text": "If we approve the budget for this environmental program, it means we are leaving the education sector to starve without funding. We have to choose: care about nature or care about our children's future.",
                    "explanation": "This argument presents two extreme choices as if there are no other options, whereas the budget could be balanced to support both environmental and educational programs.",
                    "confidence": 0.96,
                    "severity": "high",
                    "timestamp_start": None,
                    "timestamp_end": None,
                    "detailed_explanation": "False Dilemma (or bifurcation) occurs when an argument limits the available choices to two extreme options, even though there are moderate options or other solutions in between. It is often used to force the audience to choose a specific option desired by the arguer.",
                    "similar_examples": [
                        "If you do not support this war, you are an enemy of the state.",
                        "Do you want to go to college or be unemployed for the rest of your life?"
                    ],
                    "how_to_avoid": "Always look for a third alternative or middle ground. Realize that resource allocation or policy choices are rarely strictly binary."
                },
                {
                    "type": "strawman",
                    "type_label": "Strawman",
                    "text": "Environmentalists want us to go back to living in prehistoric times without technology.",
                    "explanation": "This statement misrepresents the environmentalists' position by exaggerating it to an unrealistic extreme (living in prehistoric times) to make it easier to attack.",
                    "confidence": 0.92,
                    "severity": "medium",
                    "timestamp_start": None,
                    "timestamp_end": None,
                    "detailed_explanation": "Strawman fallacy occurs when someone's argument is distorted, misrepresented, or oversimplified by an opponent to make it look weak or ridiculous, making it easier to attack and demolish.",
                    "similar_examples": [
                        "People who want to limit gun sales actually want to confiscate all self-defense tools from civilians.",
                        "He agrees we need to limit screen time for children, which means he wants our children to be technologically illiterate."
                    ],
                    "how_to_avoid": "Represent the opponent's position as accurately and honestly as possible before refuting it. If in doubt, ask for clarification first."
                }
            ],
            "overall_assessment": "The argument uses oversimplification by presenting a false binary choice and attacking a distorted version of the opponent's position.",
            "logic_score": 40
        }
    },
    {
        "input": "Exercising regularly for 30 minutes every day can help maintain heart health and improve physical fitness, according to various medical studies.",
        "output": {
            "fallacies": [],
            "overall_assessment": "This argument is logical and based on medical scientific references without any logical fallacies.",
            "logic_score": 100
        }
    }
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_formatted_few_shots(mode='quick', language='id', has_timestamps=False):
    """
    Format few-shot examples as a string based on selected mode, language, and timestamp format.
    """
    examples = FEW_SHOT_EXAMPLES if language == 'id' else FEW_SHOT_EXAMPLES_EN
    cleaned_examples = []
    
    for ex in examples:
        # Deep copy using json serialization/deserialization to prevent modifying the globals
        inp = ex["input"]
        out = json.loads(json.dumps(ex["output"]))
        
        # 1. Adjust input and output based on timestamps
        if has_timestamps:
            fallacies_types = [f["type"] for f in out.get("fallacies", [])]
            if "ad_hominem" in fallacies_types:
                # Example 1
                inp = "[00:01:10] " + inp
                for f in out["fallacies"]:
                    if f["type"] == "ad_hominem":
                        f["timestamp_start"] = 70
                        f["timestamp_end"] = 70
            elif "false_dilemma" in fallacies_types:
                # Example 2
                if language == 'id':
                    inp = ("[00:02:15] Kalau kita menyetujui anggaran untuk program lingkungan ini, berarti kita membiarkan sektor pendidikan kelaparan tanpa dana. Kita harus memilih: peduli pada alam atau peduli pada masa depan anak-anak kita. "
                           "[00:02:30] Kelompok pencinta lingkungan ingin kita kembali hidup di zaman purba tanpa teknologi.")
                else:
                    inp = ("[00:02:15] If we approve the budget for this environmental program, it means we are leaving the education sector to starve without funding. We have to choose: care about nature or care about our children's future. "
                           "[00:02:30] Environmentalists want us to go back to living in prehistoric times without technology.")
                for f in out["fallacies"]:
                    if f["type"] == "false_dilemma":
                        f["timestamp_start"] = 135
                        f["timestamp_end"] = 135
                    elif f["type"] == "strawman":
                        f["timestamp_start"] = 150
                        f["timestamp_end"] = 150
            else:
                # Example 3 (no fallacy)
                inp = "[00:03:00] " + inp
        
        # 2. Adjust based on mode (quick vs educational)
        if mode == 'quick':
            # Remove educational fields
            new_fallacies = []
            for f in out.get("fallacies", []):
                f_copy = f.copy()
                f_copy.pop("detailed_explanation", None)
                f_copy.pop("similar_examples", None)
                f_copy.pop("how_to_avoid", None)
                new_fallacies.append(f_copy)
            out["fallacies"] = new_fallacies
            
        cleaned_examples.append({
            "input": inp,
            "output": out
        })
    
    # Render string block
    result = ""
    for i, ex in enumerate(cleaned_examples, 1):
        prefix = "Contoh" if language == 'id' else "Example"
        result += f"{prefix} {i}:\n"
        result += f"Input: {ex['input']}\n"
        result += f"Output:\n{json.dumps(ex['output'], indent=2, ensure_ascii=False)}\n\n"
    return result


def build_prompt(text, mode='quick', language='id', timestamps=None):
    """
    Builds the complete logical fallacy detection prompt ready to be sent to the LLM.

    Args:
        text (str): The text or transcript to analyze.
        mode (str): Analysis mode, either 'quick' or 'educational'. Defaults to 'quick'.
        language (str): Language for the system prompt and examples, 'id' or 'en'. Defaults to 'id'.
        timestamps (bool, optional): Whether the input is a transcript with timestamps.
                                     If None, will auto-detect from the text content.

    Returns:
        str: Ready-to-send prompt combining System Prompt, Few-Shot Examples, and User Query.
    """
    # Auto-detect timestamps if not explicitly provided
    if timestamps is None:
        has_timestamps = bool(re.search(r'\[\d{1,2}:\d{2}(:\d{2})?\]', text))
    else:
        has_timestamps = bool(timestamps)
        
    # Select System Prompt based on language
    sys_prompt = SYSTEM_PROMPT_EN if language == 'en' else SYSTEM_PROMPT_ID
    
    # Select user template based on mode, timestamps, and language
    if has_timestamps:
        if mode == 'educational':
            template = EDUCATIONAL_VIDEO_PROMPT_TEMPLATE_EN if language == 'en' else EDUCATIONAL_VIDEO_PROMPT_TEMPLATE_ID
        else:
            template = VIDEO_PROMPT_TEMPLATE_EN if language == 'en' else VIDEO_PROMPT_TEMPLATE_ID
    else:
        if mode == 'educational':
            template = EDUCATIONAL_PROMPT_TEMPLATE_EN if language == 'en' else EDUCATIONAL_PROMPT_TEMPLATE_ID
        else:
            template = DETECTION_PROMPT_TEMPLATE_EN if language == 'en' else DETECTION_PROMPT_TEMPLATE_ID

    # Fetch formatted few-shot examples
    few_shots = get_formatted_few_shots(mode=mode, language=language, has_timestamps=has_timestamps)
    
    # Format the template with the provided text
    if has_timestamps:
        formatted_user_prompt = template.format(transcript_with_timestamps=text)
    else:
        formatted_user_prompt = template.format(text=text)
        
    # Construct complete prompt structure
    full_prompt = f"""{sys_prompt}

### FEW-SHOT EXAMPLES / CONTOH FEW-SHOT
{few_shots}
### USER INPUT / MASUKAN PENGGUNA
{formatted_user_prompt}"""
    
    return full_prompt
