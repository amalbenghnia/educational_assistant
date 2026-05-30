from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    role: str       
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConversationMemory:
    """
    Mémoire à fenêtre glissante.
    Garde uniquement les max_turns derniers échanges.
    Un "turn" = 1 message user + 1 réponse assistant.
    """
    session_id: str
    messages: List[Message] = field(default_factory=list)
    max_turns: int = 5  # PARAMÈTRE À EXPÉRIMENTER : 3, 5, 10

_sessions: Dict[str, ConversationMemory] = {}


def get_or_create_session(session_id: str) -> ConversationMemory:
    if session_id not in _sessions:
        _sessions[session_id] = ConversationMemory(session_id=session_id)
    return _sessions[session_id]


def add_exchange(
    session_id: str,
    user_message: str,
    assistant_response: str,
) -> None:
    """Ajoute un échange question/réponse à la mémoire."""
    memory = get_or_create_session(session_id)
    memory.messages.append(Message(role="user", content=user_message))
    memory.messages.append(Message(role="assistant", content=assistant_response))

    max_messages = memory.max_turns * 2  # *2 car user + assistant
    if len(memory.messages) > max_messages:
        memory.messages = memory.messages[-max_messages:]


def format_history(session_id: str) -> str:
    """
    Formate l'historique pour l'injecter dans le prompt.

    FORMAT :
    Utilisateur : question précédente
    Assistant : réponse précédente
    ...
    """
    memory = get_or_create_session(session_id)

    if not memory.messages:
        return ""

    lines = []
    for msg in memory.messages:
        role_label = "Utilisateur" if msg.role == "user" else "Assistant"
        lines.append(f"{role_label}: {msg.content}")

    return "\n".join(lines)


def clear_session(session_id: str) -> None:
    """Efface la mémoire d'une session."""
    if session_id in _sessions:
        del _sessions[session_id]