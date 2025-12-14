from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
import os
import pandas as pd

# Caminho do diretório persistente do ChromaDB
PERSIST_DIRECTORY = "es_gov"

# Carregando modelo de embeddings
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Função para carregar documentos a partir de um CSV com URLs
def carregar_documentos(csv_path: str):
    documents = []
    df = pd.read_csv(csv_path)
    urls = df.iloc["links"].tolist()  # Considera que a primeira coluna contém os links
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    for url in urls:
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            split_docs = splitter.split_documents(docs)
            documents.extend(split_docs)
        except Exception as e:
            print(f"Erro ao processar URL {url}: {e}")
    
    return documents

# Criação ou carregamento do banco vetorial Chroma
def criar_ou_carregar_chroma(documentos=None):
    if documentos:
        db = Chroma.from_documents(
            documents=documentos,
            embedding=embedding_model,
            persist_directory=PERSIST_DIRECTORY,
        )
        db.persist()
    else:
        db = Chroma(
            embedding_function=embedding_model,
            persist_directory=PERSIST_DIRECTORY
        )
    return db

# Execução principal
if __name__ == "__main__":
    caminho_csv = "data.csv"  # Ex: CSV com uma coluna de links
    if os.path.exists(caminho_csv):
        documentos = carregar_documentos(caminho_csv)
        db = criar_ou_carregar_chroma(documentos)
