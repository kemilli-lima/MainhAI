from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatDeepInfra
import os


os.environ["TAVILY_API_KEY"] = "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"


def busca_noticias_ufcg_web(query: str):
    """
    Busca notícias aprofundadas sobre a UFCG usando Tavily + Llama3.
    
    Args:
        query (str): Consulta sobre a UFCG.
    
    Returns:
        str: Resposta aprofundada baseada nas notícias encontradas.
    """
    tool_tavily = TavilySearchResults(k=5)  # Solicita mais resultados
    llm = ChatDeepInfra(model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.3)

    # Busca web com Tavily
    search_results = tool_tavily.run(query)

    # Organiza os resultados em texto
    if not search_results or not isinstance(search_results, list):
        return "Nenhuma notícia relevante foi encontrada."

    contexto = "\n\n".join(
        f"{i+1}. Título: {item.get('title')}\nResumo: {item.get('content')}\nLink: {item.get('url')}"
        for i, item in enumerate(search_results)
    )

    # Prompt mais elaborado
    prompt = f"""
Baseando-se nas informações a seguir extraídas da web:

{contexto}

Faça uma análise aprofundada sobre a pergunta: "{query}".
Resuma os pontos principais, destaque temas recorrentes, fatos recentes e forneça contexto adicional relevante sobre a UFCG.
Inclua datas, nomes de envolvidos e possíveis impactos quando aplicável.
"""

    return llm.invoke(prompt).content