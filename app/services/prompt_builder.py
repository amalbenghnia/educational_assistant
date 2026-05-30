SYSTEM_PROMPT = """You are an intelligent, supportive, and pedagogical AI educational assistant.
Your goal is to help students understand their coursework clearly and structurally.

ABSOLUTE RULES:
1. Answer strictly based on the provided context.
2. If the answer cannot be found in the context, clearly state: "I cannot find this information in the provided documents."
3. Always cite the source document name and page number for your answers.
4. Use clear, accessible language suited for college/university students.
5. Structure your responses with bullet points, numbered lists, or bold text where appropriate.
6. Never make up or hallucinate any facts.
"""


def build_qa_prompt(question: str, context: str) -> str:
    """Build prompt for standard RAG Q&A."""
    return f"""COURSE CONTEXT:
{context}

STUDENT QUESTION:
{question}

INSTRUCTIONS:
Answer the student's question based ONLY on the course context provided above.
Always cite the source document name and page number in parentheses at the end of relevant points. Example: (Source: Machine Learning.pdf, Page 12)
If the information is not in the context, respond with:
"I cannot find this information in the provided documents."

ANSWER:"""


def build_summary_prompt(context: str, detail_level: str = "medium") -> str:
    """
    Build prompt for document summarization.
    Supports brief, medium, detailed, bullet_point, and exam_revision formats.
    """
    instructions = {
        "brief": "Rédige un résumé explicatif concis du cours, en expliquant les concepts clés de manière claire et éducative.",
        "medium": "Rédige une explication de cours détaillée et structurée. Explique chaque concept en profondeur avec des phrases complètes, pas juste des mots-clés. Divise en : Introduction, Explications détaillées des concepts, et Conclusion.",
        "detailed": "Rédige un cours complet et détaillé basé sur le document. Pour chaque chapitre ou section, fournis une explication pédagogique complète, explique les formules, les théories et donne des détails. N'utilise pas seulement des listes à puces, écris de vrais paragraphes explicatifs.",
        "bullet_point": "Extrais toutes les définitions importantes et le vocabulaire, et explique-les en détail sous forme de liste.",
        "exam_revision": "Génère des notes de révision détaillées pour un examen, en expliquant clairement chaque point important."
    }
    
    instruction = instructions.get(detail_level, instructions["medium"])
    
    return f"""DOCUMENT CONTENT:
{context}

INSTRUCTION:
{instruction}
Base your response strictly on the provided content. Keep technical terminology intact.

SUMMARY:"""


def build_quiz_prompt(context: str, num_questions: int = 5, difficulty: str = "intermediate", qtype: str = "mixed") -> str:
    """
    Build prompt for generating structured quizzes.
    Instructs the LLM to output a clean JSON structure to facilitate backend parsing.
    """
    type_instruction = {
        "mcq": "Generate only Multiple Choice Questions (MCQ) with 4 options (A, B, C, D).",
        "true_false": "Generate only True/False questions (options must be A: True, B: Faux or A: True, B: False).",
        "short_answer": "Generate only short essay questions that require a brief text answer. Define the correct answer as the key criteria/model response.",
        "fill_blank": "Generate only Fill-in-the-blank questions (use '___' inside the question where the term belongs).",
        "mixed": "Generate a mixed set of questions including MCQs, True/False, Short Answer, and Fill-in-the-blank questions."
    }
    
    selected_type_instr = type_instruction.get(qtype, type_instruction["mixed"])
    
    return f"""COURSE CONTEXT:
{context}

INSTRUCTIONS:
Génère exactement {num_questions} questions de quiz en FRANÇAIS basées sur le contexte du cours.
Niveau de difficulté : {difficulty.upper()} (Beginner = rappel simple, Intermediate = application, Advanced = synthèse & analyse).
Type de question : {qtype.upper()}. {selected_type_instr}

Tu DOIS retourner UNIQUEMENT un texte JSON valide (aucun texte avant, aucun markdown, aucun commentaire). La structure JSON doit correspondre EXACTEMENT à ce format :

{{
  "questions": [
    {{
      "id": 1,
      "type": "mcq",
      "question": "Quelle est la capitale de la France ?",
      "options": {{"A": "Berlin", "B": "Londres", "C": "Paris", "D": "Madrid"}},
      "correct": "C",
      "explanation": "Paris est la capitale et la plus grande ville de France.",
      "page_reference": 5
    }}
  ]
}}

Assure-toi que les options sont correctes et que le JSON est syntaxiquement valide.
JSON:"""


def build_flashcard_prompt(context: str) -> str:
    """Build prompt for flashcards generation."""
    return f"""COURSE CONTEXT:
{context}

INSTRUCTIONS:
Extrais les concepts éducatifs, le vocabulaire et les théories les plus importants du contexte ci-dessus.
Génère une liste de flashcards d'étude en FRANÇAIS.
Tu DOIS retourner UNIQUEMENT un tableau JSON valide (pas de markdown, pas d'explications). La structure JSON doit être EXACTEMENT :

[
  {{
    "front": "Terme ou Question",
    "back": "Définition ou réponse courte (1-2 phrases)",
    "topic": "Catégorie générale (ex: Régression, RSE)"
  }}
]

Génère entre 8 et 12 flashcards de haute qualité. Ne mets AUCUN texte avant ou après le JSON.
JSON:"""


def build_exam_prep_prompt(context: str, prep_type: str, difficulty: str = "intermediate") -> str:
    """
    Build prompt for generating exam preparation material.
    Supports practice_exam, mock_test, expected_questions, important_topics, and revision_plans.
    """
    prep_instructions = {
        "practice_exam": "Generate a practice exam sheet containing 5 structured exam questions (analytical/computational/essay) followed by detailed model solutions.",
        "mock_test": "Generate a mock exam paper with standard academic guidelines (e.g., Time Allowed: 2 Hours, Instructions, Total Marks) and a list of questions (without immediate solutions, just the questions).",
        "expected_questions": "Identify 5 highly probable exam questions that could be asked based on this material, and write exemplary high-scoring answers for each.",
        "important_topics": "Analyze the text and extract the high-yield topics most likely to appear on an exam. Provide a brief summary of what is essential to master for each topic.",
        "revision_plan": "Generate a customized study revision plan (e.g., 5-day step-by-step checklist) detailing what sections to focus on, what to practice, and active recall suggestions."
    }
    
    instruction = prep_instructions.get(prep_type, prep_instructions["practice_exam"])
    
    return f"""COURSE CONTEXT:
{context}

INSTRUCTIONS:
You are preparing exam material for a student.
Difficulty Level: {difficulty.upper()} (Beginner = basic terms, Intermediate = conceptual problems, Advanced = deep analysis and case studies).
Task: {instruction}

Write the output in highly professional academic Markdown. Include clear headers and formatting.

EXAM MATERIAL:"""