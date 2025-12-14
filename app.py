from agents.agents.agents import GRAPH
from flask import Flask, request, render_template, jsonify
from langchain_core.messages import HumanMessage
import asyncio
from agents.agents.criar_resumo import criar_resumo
from dotenv import load_dotenv
from agents.tratar_arquivos.main import realizar_tratamento_dos_arquivos

load_dotenv(override=True)


app = Flask(__name__, static_url_path="/static")
system = GRAPH

"""_summary_
Retorna a página HTML de chat a ser renderizada.

Returns:
    Any: Retorna a página de chat.
"""
@app.route('/')
def home():
    return render_template('index.html')


"""_summary_
Deleta um chat já criado pelo usuário.

Returns:
    dict: Retorna uma mensagem 'apagado' e o status OK informado que o chat foi deletado. 
"""
@app.route('/delete_chat', methods=["POST"])
def delete_chat() -> dict:
    return jsonify({"msg": "apagado"}), 200


"""_summary_
Abre uma conexão HTTP com o frontend para receber a pergunta e retorna um resumo 
para ser renderizado no Front-End sobre o tópico abordado.
O resumo contém 3 palavras e será mostrado no drawer como titulo da conversa.

Returns:
    dict: Retorna um resumo da conversa com até 3 palavras.
"""
@app.route('/resumir', methods=["POST"])
def resumir() -> dict:
    data = request.get_json()
    if not data or 'texto' not in data:
        return jsonify({"erro": "Campo 'texto' é obrigatório"}), 400
    
    texto = data['texto']
    
    try:
        resumo = criar_resumo(texto)
        print(f"Resumo gerado: {resumo['titulo']}") 

        return jsonify({"resumo": resumo['titulo']}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao gerar resumo: {str(e)}"}), 500


"""_summary_
Função assincrona que usará os agentes para responder a pergunta do usuário.
"""
async def process_query(query):
    """
    Processa a consulta do usuário usando o sistema de agentes.
    """
    config = {"configurable": {"thread_id": "1"}}
    inputs = {"messages": [HumanMessage(content=query)]}
    response = []

    async for chunk in system.astream(inputs, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
        response.append(chunk["messages"][-1].content)
    
    return response[-1] if response else "Desculpe, não consegui processar sua solicitação."


"""_summary_
Função que recebe uma entrada para os agentes processar e respoonder a pergunta do usuário.

Returns:
    Any: Retorna a resposta dos agentes que respondem a pergunta feita pelo usuário.
"""
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('input_data')
    arquivos = request.files.getlist('archives[]')

    print(f"Mensagem recebida: {user_message}")
    print(f"{len(arquivos)} arquivo(s) recebido(s): {[file.filename for file in arquivos]}")
    
    if len(arquivos) > 0:
        user_message += f"{user_message}\n\n{realizar_tratamento_dos_arquivos(arquivos)}"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_message = loop.run_until_complete(process_query(user_message))
    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")
        bot_message = "Desculpe, ocorreu um erro ao processar sua solicitação."

    return {'response': bot_message}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)