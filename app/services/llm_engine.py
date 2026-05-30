import ollama
from typing import Generator
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


def generate_response(
    prompt: str,
    system_prompt: str = "",
    stream: bool = False,
) -> str:
    """
    Envoie un prompt à Ollama et retourne la réponse complète.

    PARAMÈTRE stream=False :
    Attend que le LLM finisse TOUT avant de retourner.
    Plus simple à utiliser.

    PARAMÈTRE stream=True :
    Retourne les tokens au fur et à mesure (voir generate_stream).
    Meilleure expérience utilisateur pour les longues réponses.
    MOT-CLÉ : "streaming LLM response", "Server-Sent Events FastAPI"
    """
    logger.info(f"Génération LLM | modèle={settings.llm_model}")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=messages,
            options={
                "temperature": settings.llm_temperature,
                # num_ctx : combien de tokens le modèle peut "voir"
                # Plus grand = peut traiter plus de contexte
                # Mais utilise plus de RAM
                "num_ctx": 4096,
                # top_p et top_k : contrôlent la distribution de probabilité
                # EXPÉRIMENTE ces valeurs
                "top_p": 0.9,
                "top_k": 40,
            },
        )
        return response["message"]["content"]

    except Exception as e:
        logger.error(f"Erreur Ollama : {e}")
        raise RuntimeError(
            f"Erreur LLM. Vérifie qu'Ollama tourne et que le modèle "
            f"'{settings.llm_model}' est installé. Commande : "
            f"ollama pull {settings.llm_model}"
        )


def generate_stream(
    prompt: str,
    system_prompt: str = "",
) -> Generator[str, None, None]:
    """
    Version streaming : yield les tokens au fur et à mesure.

    Utilisé avec FastAPI StreamingResponse pour une UX fluide.
    L'utilisateur voit la réponse s'écrire en temps réel.

    MOT-CLÉ : "FastAPI StreamingResponse", "async generator Python"
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    stream = ollama.chat(
        model=settings.llm_model,
        messages=messages,
        stream=True,
        options={"temperature": settings.llm_temperature, "num_ctx": 4096},
    )

    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token