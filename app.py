import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai  
import fitz


app = Flask(__name__)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env")

genai.configure(api_key=api_key)  

model = genai.GenerativeModel('gemini-2.5-flash')  


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

@app.route('/resumir-pdf', methods=['POST'])
def resumir_pdf():
    # 1. Verificar se o ficheiro foi enviado
    if 'pdf_file' not in request.files:
        return jsonify({"erro": "Nenhum ficheiro PDF enviado"}), 400

    file = request.files['pdf_file']

    # 2. Verificar se o nome do ficheiro está vazio
    if file.filename == '':
        return jsonify({"erro": "Nenhum ficheiro selecionado"}), 400
    
    # 3. Verificar se o ficheiro é um PDF
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # 4. Ler o conteúdo do PDF em memória
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            
            # 5. Extrair o texto de todas as páginas
            texto_extraido = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                texto_extraido += page.get_text()
            
            pdf_document.close()

            # Se não houver texto, avise o utilizador
            if not texto_extraido.strip():
                 return jsonify({"resumo": "O PDF parece estar vazio ou contém apenas imagens."})

            # 6. Obter opções de resumo e montar o prompt (reaproveitando sua função!)
            formato = request.form.get("formato")
            detalhe = request.form.get("detalhe")
            
            prompt = montagem_prompt(texto_extraido, formato, detalhe)
            response = model.generate_content(prompt)
            return jsonify({"resumo": response.text})

        except Exception as e:
            print(f"Erro ao processar PDF: {e}") # Log do erro no servidor
            return jsonify({"erro": "Falha ao ler o ficheiro PDF."}), 500

    return jsonify({"erro": "Formato de ficheiro inválido. Por favor, envie um PDF."}), 400



#if __name__ == '__main__':
#    app.run(debug=True)
