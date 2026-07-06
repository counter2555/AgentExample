# Zyklische Text-Schleife (Multi-Agenten-System)

Ein interaktives Multi-Agenten-System, das mithilfe von **LangGraph**, **LangChain** und **Chainlit** einen zyklischen Redaktionsprozess simuliert. Ein **Autor-Agent** verfasst und überarbeitet Texte zu einem frei wählbaren Thema, während ein **Lektor-Agent** (unter Nutzung von *Structured Output*) den Text so lange kritisiert und optimiert, bis er absolut zufrieden ist.

## Funktionsweise

Das System basiert auf einem gerichteten Graphen (StateGraph), der eine Feedbackschleife zwischen zwei spezialisierten KI-Agenten etabliert:

1. **Autor (Node):** Erstellt einen initialen Textentwurf oder überarbeitet den bestehenden Entwurf basierend auf dem Feedback des Lektors.
2. **Lektor (Node):** Analysiert den Text kritisch. Er liefert strukturiertes Feedback, einen eigenen Optimierungsvorschlag und entscheidet (`is_satisfied: True/False`), ob der Text den Qualitätsansprüchen genügt.
3. **Router (Conditional Edge):** Prüft den Status von `is_satisfied`. Wenn `False`, geht es zurück zum Autor (Nachbesserung). Wenn `True`, wird der Workflow erfolgreich beendet (`END`).

> **Sicherheitsnetz:** Um endlose Schleifen bei uneinigen Agenten zu verhindern, ist das `recursion_limit` in LangGraph auf maximal 10 Iterationen eingestellt. Da das eingesetzte **GPT-5.1** Modell intern Denkschritte (Reasoning Tokens) generiert, wird das Token-Budget pro Aufruf über `max_completion_tokens` abgesichert.

---

## Tech-Stack

* **Backend / Agenten-Logik:** LangGraph und LangChain
* **LLM-Infrastruktur:** Azure AI Foundry (Modell: `gpt-5.1-codex-mini`)
* **UI-Framework:** Chainlit
* **Paketmanagement:** Poetry / Pyproject

---

## Installation & Setup

### 1. Voraussetzungen

Stelle sicher, dass du Python `3.13` installiert hast (wie in der `pyproject.toml` definiert).

### 2. Repository klonen & Abhängigkeiten installieren

Nutze dein bevorzugtes Tool (z. B. Poetry), um die virtuelle Umgebung zu erstellen und die Abhängigkeiten (inklusive der Azure-Erweiterung für LangChain) zu installieren:

```bash
# Wenn du Poetry nutzt:
poetry install

```

*Hinweis: Für Azure AI Foundry wird das Paket `langchain-azure-ai` verwendet.*

### 3. Umgebungsvariablen konfigurieren

Erstelle eine `.env`-Datei im Wurzelverzeichnis oder exportiere die Variablen in deinem Terminal. Die Projektdaten findest du im **Azure AI Foundry Portal** unter den Projekteigenschaften deines Workspace.

```bash
# Die vollständige Projekt-Inferenz-URL aus Azure AI Foundry (endet oft auf /openai/v1)
export AZURE_AI_PROJECT_ENDPOINT="https://<dein-projektname>.<region>.services.ai.azure.com/openai/v1"

# Dein geheimer API-Schlüssel für das Projekt
export AZURE_AI_PROJECT_KEY="dein-foundry-projekt-api-key"

# Optional: Die verwendete API-Version
export AZURE_OPENAI_API_VERSION="2025-11-13"
```

---

## Code-Integration (Wichtige Besonderheiten)

Da das System auf das **gpt-5.1-codex-mini** Reasoning-Modell migriert wurde, müssen die Agenten im Code über die Klasse `AzureAIOpenAIApiChatModel` initialisiert werden.

Achte darauf, anstelle des veralteten `max_tokens` den Parameter `max_completion_tokens` zu verwenden, da das Modell Platz für seine internen Denkschritte benötigt:

```python
import os
from langchain_azure_ai.chat_models import AzureAIOpenAIApiChatModel

llm = AzureAIOpenAIApiChatModel(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=os.getenv("AZURE_AI_PROJECT_KEY"),
    model="gpt-5.1-codex-mini",
    max_completion_tokens=4096,  # Deckt Denkprozess + finalen Text ab
    model_kwargs={
        "reasoning_effort": "low" # 'low' oder 'minimal' reicht für schnelle Redaktionsschleifen
    }
)

```