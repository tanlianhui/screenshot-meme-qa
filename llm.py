import os
os.environ["OLLAMA_HOST"] = "http://192.168.1.221:11434"
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.3-70B")
# QA
def qa(query: str):
    rag_options: list[str] = [""]
    results = llm.invoke(f"Judging from the user query '{query}', what is its most suitable response in the following options: '{rag_options}'.")
    return results.content

# Paraphrase
def paraphrase(query: str):
    rag_options: list[str] = [""]
    results = llm.invoke(f"Judging from the user query '{query}', what is its most similar response in the following options: '{rag_options}'.")
    return results.content