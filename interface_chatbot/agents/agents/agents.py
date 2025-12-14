from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Union, List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import os

# Prompts
from agents.agents.prompts import PROMPT_AGENTE_SUPERVISOR, PROMPT_AGENTE_ES_GOV, PROMPT_AGENTE_AGREGADOR

# Carregar variáveis de ambiente
load_dotenv()
#os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Inicialização do LLM
# llm_google = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
llm_google = ChatOpenAI(model="gpt-4", temperature=0.3)

# Caminho do diretório ChromaDB persistente
PERSIST_DIRECTORY = "es_gov"

# Embeddings e banco Chroma
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(embedding_function=embedding_model, persist_directory=PERSIST_DIRECTORY)

# Estado do grafo
class GraphState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    content: str

# Agente ES GOV com RAG
def agente_es_gov(state: GraphState) -> GraphState:
    user_question = next(
        (msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)),
        "Nenhuma pergunta encontrada."
    )

    # Busca por similaridade no banco Chroma
    docs = vectorstore.similarity_search(user_question, k=7)

    # Constrói o contexto com os documentos recuperados
    context_parts = [doc.page_content for doc in docs]
    context_text = "\n\n".join(context_parts)

    # Montagem do prompt com contexto
    prompt_text = PROMPT_AGENTE_ES_GOV.replace("{PERGUNTA_DO_USUÁRIO}", user_question)
    prompt_text_2 = prompt_text.replace("{CONTEXTO}", context_text)

    prompt = [SystemMessage(content=prompt_text_2)] + state["messages"]
    response = llm_google.invoke(prompt)

    # Atualização do estado
    state["messages"].append(AIMessage(content=response.content))
    state["content"] = response.content
    return state

# Construção do grafo
builder = StateGraph(GraphState)
builder.add_node("agente_es_gov", agente_es_gov)
builder.set_entry_point("agente_es_gov")
builder.add_edge("agente_es_gov", END)
GRAPH = builder.compile()
