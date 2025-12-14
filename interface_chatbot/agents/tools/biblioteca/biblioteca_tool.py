from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from typing import Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
import numpy as np
import json
from ...agents.tempo_execucao import medir_tempo_execucao_tool_call

llm = ChatOllama(model="llama3.2:3b", temperature=0)
model_sentence = SentenceTransformer("all-MiniLM-L6-v2")


def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def get_most_similar(lista_a_comparar: list, dado_comparado: str, top_k: int, limiar: float) -> tuple:
    """
    Faz a comparação entre uma lista contendo dicionários com informações relevantes com o dado a ser comparado e retorna os top K mais prováveis.
    lista_a_comparar: 
    [
    {
        descricao: "Descrição do documento",
        indice_do_documento: 10,
        indice_chunk_do_documento: 1
    }, 
    ...
    ]

    Args:
        lista_a_comparar (list): Lista contendo dicionários com informações relevantes.
        dado_comparado (str): Dado a ser comparado.
        top_k (int): Número de informações mais similar.
        mapper (dict): Mapeamento da nomenclatura será recebida para retornar no padrão usado pelo RAG para a LLM.
        limiar (float): Nível de similaridade.

    Returns:
        tuple: Retorna os top K mais prováveis.
    """
    
    descricao = [remover_acentos(i["descricao"].lower().strip()) for i in lista_a_comparar]
    embeddings = model_sentence.encode(descricao)
    embedding_query = model_sentence.encode(dado_comparado.lower().strip()).reshape(1, -1)

    similarities = cosine_similarity(embeddings, embedding_query).flatten()
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]
    
    top_k = [{"documento": lista_a_comparar[idx], "similaridade_cosseno": similarities[idx]} for idx in top_k_indices]
    
    possiveis_k = []
    for k in top_k:
        if k['similaridade_cosseno'] >= limiar:
            possiveis_k.append(k)
    
    return possiveis_k, top_k


@tool
@medir_tempo_execucao_tool_call
def get_livro_biblioteca(assunto: Any) -> dict:
    """
    Busca livros da biblioteca sobre algum assunto.

    Args:
        assunto (Any): Assunto buscado.
    
    Returns:
        dict: Retorna o livro mais similar.
    """

    assunto = str(assunto)
    lista_a_comparar = []
    with open("./agents/tools/biblioteca/chunks.json", "r", encoding="utf-8") as livros:
        lista_a_comparar = json.loads(livros.read())
        if not isinstance(lista_a_comparar, list):
            raise ValueError("Arquivo chunks.json deve conter uma lista de dicionários")
    
    chunks_mais_similares = get_most_similar(lista_a_comparar=lista_a_comparar, dado_comparado=assunto, top_k=5, limiar=0.7)
    format = """{'indice_do_documento': '', 'indice_chunk_do_documento': ''}"""

    descricao_agente = f"""
        Para o livro que aborda o seguinte assunto: '{assunto}', quais desses possíveis tópicos abaixo é mais similar ao assunto do nome informado?
        
        {chunks_mais_similares}
        
        Responda no seguinte formato:
        
        {format}
        
        Não adicione mais nada, apenas a resposta nesse formato (codigo e nome).
    """

    response = llm.invoke(descricao_agente)
    livro_provavel = json.loads((response.content).replace("'", '"'))
    documentos = [documento["documento"] for documento in chunks_mais_similares[1]]
    documentos = [
        item["descricao"] for item in documentos
        if item['indice_do_documento'] == livro_provavel["indice_do_documento"] and 
        item['indice_chunk_do_documento'] == livro_provavel["indice_chunk_do_documento"]
    ]
    print(documentos)
    return str(documentos)