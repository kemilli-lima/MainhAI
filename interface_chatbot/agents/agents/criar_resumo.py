import json
from langchain_community.chat_models import ChatDeepInfra

def criar_resumo(texto: str) -> str:
    try:
        llm = ChatDeepInfra(model="meta-llama/Meta-Llama-3.1-8B-Instruct", temperature=0)
        resposta = llm.invoke(
            f"""
            Gere um título de até 3 palavras para o texto a seguir:
            '{texto}'
            
            *IMPORTANTE*:
            - Você sempre deve gerar um título, não faça nada além disso.
            - Sempre gere no seguinte formato: {{"titulo": "titulo_gerado"}}
            """
        )

        resumo = resposta.content if hasattr(resposta, "content") else str(resposta)
        resumo = resumo.replace("'", '"')
        resumo = json.loads(resumo)
        
        return resumo
    except Exception as e:
        raise(e)