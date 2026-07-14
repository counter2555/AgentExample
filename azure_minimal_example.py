import os
from langchain_azure_ai.chat_models import AzureAIOpenAIApiChatModel
from langchain_core.prompts import ChatPromptTemplate

llm = AzureAIOpenAIApiChatModel(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=os.getenv("AZURE_AI_PROJECT_KEY"),
    model="gpt-5.1-codex-mini",       
    max_completion_tokens=512,       
    model_kwargs={
        "reasoning_effort": "low"
    }
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Du bist ein einfacher Coding Agent. Du antwortest so kurz wie möglich."),
    ("user", "Schreibe ein Python Hello-World Programm.")
])

chain = prompt | llm

if __name__ == "__main__":
    print("Connecting to Azure AI Foundry model endpoint...")
    
    response = chain.invoke({"topic": "Hello World from Azure AI Foundry!"})
    
    print("\n--- Model Code Output ---")
    print(response.content)
    
    print("\n--- Metadata & Reasoning Tokens ---")
    print(response.usage_metadata)
