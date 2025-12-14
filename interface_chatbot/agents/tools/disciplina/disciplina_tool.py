from langchain_core.tools import tool
import json, requests
from ...agents.tempo_execucao import medir_tempo_execucao_tool_call

@tool
@medir_tempo_execucao_tool_call
def get_disciplina() -> list:
    """
    _summary_
    Busca as disciplinas da grade do curso de Ciência da Computação da UFCG.

    Returns:
        Retorna todas as disciplinas da grade do curso de Ciência da Computação da UFCG.

    """

    response = requests.get("https://eureca.sti.ufcg.edu.br/das/v2/disciplinas?status=ATIVOS&curso=14102100&curriculo=2023")
    if response.status_code == 200:
        disciplinas = ", ".join([disciplina["nome"] for disciplina in json.loads(response.text)])
        return disciplinas
    return [{"msg": "error", "content": json.loads(response)}]


@tool
@medir_tempo_execucao_tool_call
def get_informacao_disciplina() -> list[dict]:
    """
    _summary_
    Retorna as informações de apenas uma disciplina de teoria da computação.
    """

    response = requests.get("https://eureca.sti.ufcg.edu.br/das/v2/disciplinas?status=ATIVOS&curso=14102100&curriculo=2023&disciplina=1411171")
    if response.status_code == 200:
        return json.loads(response.text)
    return [{"msg": "error", "content": json.loads(response)}]