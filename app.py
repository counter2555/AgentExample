import os
from typing import TypedDict
import chainlit as cl
from pydantic import BaseModel, Field

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# Konfiguration & LLM Setup
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")

llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.7,
)


# State & Pydantic Modelle
class AgentState(TypedDict):
    topic: str
    draft: str
    feedback: str
    is_satisfied: bool


# Pydantic Modell
class EditorReview(BaseModel):
    feedback: str = Field(
        description="Detaillierte Kritik und konkrete Verbesserungsvorschläge zum Entwurf. Wenn alles perfekt ist, halte dich kurz."
    )
    improved_text: str = Field(description="Der überarbeitete Text.")
    is_satisfied: bool = Field(
        description="MUSS 'True' sein, wenn der Text absolut fehlerfrei, stilistisch top und fertig ist. MUSS 'False' sein, wenn der Text noch Schwächen hat und der Autor nachbessern MUSS."
    )


# Agenten (Nodes im Graphen)
def author_node(state: AgentState) -> AgentState:
    """Agent 1: Schreibt den Entwurf ODER verbessert ihn basierend auf Feedback."""
    topic = state["topic"]
    current_draft = state.get("draft", "")
    feedback = state.get("feedback", "")

    # Wenn noch kein Entwurf existiert -> Erster Versuch
    if not current_draft:
        messages = [
            SystemMessage(
                content="Du bist ein kreativer Autor. Schreibe einen kurzen, spannenden Absatz zum vorgegebenen Thema."
            ),
            HumanMessage(content=f"Thema: {topic}"),
        ]
    # Wenn Feedback existiert -> Iteration / Verbesserung
    else:
        messages = [
            SystemMessage(
                content="Du bist ein einsichtiger Autor. Verbessere deinen vorherigen Entwurf basierend auf dem strengen Feedback deines Lektors. Versuche alle Kritikpunkte exakt umzusetzen!"
            ),
            HumanMessage(
                content=f"Thema: {topic}\n\nDein vorheriger Entwurf:\n{current_draft}\n\nFeedback vom Lektor:\n{feedback}"
            ),
        ]

    response = llm.invoke(messages)
    return {"draft": response.content}


def editor_node(state: AgentState) -> AgentState:
    """Agent 2: Analysiert den Entwurf und entscheidet, ob er zufrieden ist."""
    draft = state["draft"]

    messages = [
        SystemMessage(
            content="Du bist ein kritischer, aber fairer Lektor. Prüfe den Text genau. Wenn er noch gravierende Mängel hat, setze 'is_satisfied' auf False. Wenn er gut ist, setze 'is_satisfied' auf True."
        ),
        HumanMessage(content=f"Hier ist der Entwurf zur Prüfung:\n\n{draft}"),
    ]

    structured_llm = llm.with_structured_output(EditorReview)
    review: EditorReview = structured_llm.invoke(messages)

    return {
        "feedback": review.feedback,
        "draft": review.improved_text,  # Wir überschreiben den Draft direkt mit der vom Lektor korrigierten Basis
        "is_satisfied": review.is_satisfied,
    }


# Routing & Graph Definition (Langgraph)
def router_logic(state: AgentState):
    """Prüft den State und entscheidet, wo es als nächstes hingeht."""
    if state["is_satisfied"]:
        return "beenden"
    else:
        return "nachbessern"


def build_graph():
    workflow = StateGraph(AgentState)

    # Nodes hinzufügen
    workflow.add_node("Autor", author_node)
    workflow.add_node("Lektor", editor_node)

    # Start-Kante
    workflow.add_edge(START, "Autor")
    workflow.add_edge("Autor", "Lektor")

    workflow.add_conditional_edges(
        "Lektor",
        router_logic,
        {
            "nachbessern": "Autor",  # Wenn router_logic "nachbessern" zurückgibt -> Gehe zu Autor
            "beenden": END,  # Wenn router_logic "beenden" zurückgibt -> Gehe zu END
        },
    )

    return workflow.compile()


# UI Integration (Chainlit)
@cl.on_chat_start
async def on_chat_start():
    app = build_graph()
    cl.user_session.set("graph_app", app)
    await cl.Message(
        content="Willkommen in der zyklischen Text-Schleife! \nNenne ein Thema. Der Autor schreibt und der Lektor kritisiert so lange, bis er 100% zufrieden ist."
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    app = cl.user_session.get("graph_app")

    initial_state = {
        "topic": message.content,
        "draft": "",
        "feedback": "",
        "is_satisfied": False,
    }

    config = {"recursion_limit": 10}

    try:
        async for event in app.astream(initial_state, config=config):
            for node_name, node_state in event.items():

                if node_name == "Autor":
                    await cl.Message(
                        content=f"**Autor (Überarbeitung/Entwurf):**\n{node_state.get('draft')}",
                        author="Autor-Agent",
                    ).send()

                elif node_name == "Lektor":
                    status_text = (
                        "ZUFRIEDEN! Workflow beendet."
                        if node_state.get("is_satisfied")
                        else "NICHT ZUFRIEDEN! Zurück zum Autor."
                    )

                    msg = cl.Message(
                        content=f"**Lektor Urteil: {status_text}**\n\n"
                        f"**Kritik/Feedback:**\n{node_state.get('feedback')}\n\n"
                        f"**Aktueller Textstand:**\n{node_state.get('draft')}",
                        author="Lektor-Agent",
                    )
                    await msg.send()

    except Exception as e:
        # Fängt das Überschreiten des Recursion Limits ab
        if "recursion limit" in str(e).lower():
            await cl.Message(
                content="**Abbruch:** Das maximale Limit an Überarbeitungen (Recursion Limit) wurde erreicht, da sich Autor und Lektor uneinig waren!"
            ).send()
        else:
            raise e
