import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai  # <- use este import


app = Flask(__name__)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env")

genai.configure(api_key=api_key)  # <- essa linha só funciona com o import certo

model = genai.GenerativeModel('gemini-2.5-flash')  # <- usa a variável 'genai' com o modelo


def montagem_prompt(texto, formato, detalhe):
    # Princípio 16: Atribuir um papel ao modelo
    instrucao_persona = "Você é um especialista em análise e síntese de informações."

    # Princípio 9: Aumentar a objetividade 
    # Princípio 4: Usar diretivas afirmativas 
    # Princípio 25: Declarar requisitos específicos 
    instrucao_tarefa = f"Sua tarefa é criar um resumo do texto fornecido. Você DEVE seguir estritamente as seguintes regras de formato e detalhe:"


    # Traduzindo as escolhas do usuário em instruções claras
    if formato == "Parágrafos":
        instrucao_formato = "- Formato do Resumo: O resumo DEVE ser apresentado em parágrafos bem estruturados e coesos."
    elif formato == "Linha do Tempo":
        instrucao_formato = "- Formato do Resumo: O resumo DEVE ser organizado como uma linha do tempo, destacando os eventos em ordem cronológica."
    else: # Lista Ordenada
        instrucao_formato = "- Formato do Resumo: O resumo DEVE ser uma lista ordenada ou de tópicos (bullet points, porem não use asterisco para enumerar os tópicos), com os pontos mais importantes no início."

    if detalhe == "Conciso":
        instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ser conciso e direto, contendo apenas os pontos mais cruciais (aproximadamente 2-3 frases ou itens)."
    elif detalhe == "Detalhado":
        instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ser detalhado e abrangente, cobrindo todos os aspectos relevantes do texto original."
    else: # Médio
        instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ter um equilíbrio entre concisão e profundidade, capturando as ideias principais sem se estender excessivamente."

    # Princípios 8 e 17: Formatar e usar delimitadores para clareza

    return f"""
    ## INSTRUÇÃO ##
    {instrucao_persona}
    {instrucao_tarefa}
    {instrucao_formato}
    {instrucao_detalhe}

    ## TEXTO ORIGINAL ##
    ---
    {texto}
    ---
    """


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/resumir', methods=['POST'])
def resumir():
    data = request.json
    texto = data.get("texto")
    formato = data.get("formato")
    detalhe = data.get("detalhe")

    if not all([texto, formato, detalhe]):
        return jsonify({"erro": "Dados incompletos"}), 400

    prompt = montagem_prompt(texto, formato, detalhe)
    response = model.generate_content(prompt)
    return jsonify({"resumo": response.text})


if __name__ == '__main__':
    app.run(debug=True)
