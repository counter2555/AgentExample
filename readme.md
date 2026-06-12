# Zyklische Text-Schleife (Multi-Agenten-System)

Ein interaktives Multi-Agenten-System, das mithilfe von **LangGraph**, **LangChain** und **Chainlit** einen zyklischen Redaktionsprozess simuliert. Ein **Autor-Agent** verfasst und überarbeitet Texte zu einem frei wählbaren Thema, während ein **Lektor-Agent** (unter Nutzung von *Structured Output*) den Text so lange kritisiert und optimiert, bis er absolut zufrieden ist.

## Funktionsweise

Das System basiert auf einem gerichteten Graphen (StateGraph), der eine Feedbackschleife zwischen zwei spezialisierten KI-Agenten etabliert:

1. **Autor (Node):** Erstellt einen initialen Textentwurf oder überarbeitet den bestehenden Entwurf basierend auf dem Feedback des Lektors.
2. **Lektor (Node):** Analysiert den Text kritisch. Er liefert strukturiertes Feedback, einen eigenen Optimierungsvorschlag und entscheidet (`is_satisfied: True/False`), ob der Text den Qualitätsansprüchen genügt.
3. **Router (Conditional Edge):** Prüft den Status von `is_satisfied`. Wenn `False`, geht es zurück zum Autor (Nachbesserung). Wenn `True`, wird der Workflow erfolgreich beendet (`END`).

> **Sicherheitsnetz:** Um endlose Schleifen bei uneinigen Agenten zu verhindern, ist das `recursion_limit` in LangGraph auf maximal 10 Iterationen eingestellt.

---

## Tech-Stack

* **Backend / Agenten-Logik:** Langgraph und Langchain
* **LLM:** Mistral AI
* **UI-Framework:** Chainlit
* **Paketmanagement:** Poetry / Pyproject

---

## Installation & Setup

### 1. Voraussetzungen
Stelle sicher, dass du Python `3.13` installiert hast (wie in der `pyproject.toml` definiert).

### 2. Repository klonen & Abhängigkeiten installieren
Nutze dein bevorzugtes Tool (z. B. Poetry), um die virtuellen Umgebung zu erstellen und die Abhängigkeiten zu installieren:

```bash
# Wenn du Poetry nutzt:
poetry install
```