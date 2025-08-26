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

model = genai.GenerativeModel('gemini-1.5-flash')


def montagem_prompt(texto, formato, detalhe):
    """
    Monta um prompt acadêmico especializado.
    - formato: Controla se o resumo é Extrativo ou o estilo de apresentação do Abstrativo.
    - detalhe: Controla a profundidade/estilo do resumo.
    """
    
    instrucao_persona = "Você é um pesquisador acadêmico assistente, especializado em analisar e sintetizar artigos científicos de forma estruturada."

    if formato == "Extrativo":
        
        if detalhe == "indicativo":
            num_frases = 3
            tarefa_especifica = f"Sua tarefa é criar um resumo EXTRATIVO INDICATIVO. Selecione as {num_frases} sentenças mais essenciais para dar uma ideia geral do conteúdo."
        else:  
            num_frases = 6
            tarefa_especifica = f"Sua tarefa é criar um resumo EXTRATIVO INFORMATIVO. Selecione as {num_frases} sentenças mais importantes que cobrem os pontos principais do texto."
        
        regras = """Você DEVE seguir estritamente as seguintes regras:
1. A saída DEVE ser composta APENAS por frases copiadas verbatim (palavra por palavra) do texto original.
2. NÃO reescreva, parafraseie ou adicione qualquer palavra que não esteja no texto original."""

        return f"""
{instrucao_persona}

{tarefa_especifica}

{regras}

## TEXTO ORIGINAL ##
---
{texto}
---
"""
    else:
        instrucao_tarefa = """Sua tarefa é criar um resumo técnico e ABSTRATIVO do artigo científico fornecido.
Primeiro, analise o texto para identificar as seguintes seções chave: Objetivos, Metodologia, Resultados Principais e Conclusão."""

        if formato == "Tópicos":
            instrucao_apresentacao = "Apresente o resumo final em formato de TÓPICOS (bullet points)."
        elif formato == "Linha do Tempo":
            instrucao_apresentacao = "Apresente o resumo final em formato de LINHA DO TEMPO, se aplicável ao conteúdo."
        else: # Parágrafos
            instrucao_apresentacao = "Apresente o resumo final em formato de PARÁGRAFOS coesos."

        if detalhe == "indicativo":
            instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ser de caráter indicativo (cerca de 20% do original), apontando os temas principais sem aprofundar."
        elif detalhe == "critico":
            instrucao_detalhe = """- Nível de Detalhe: O resumo DEVE ser de caráter CRÍTICO. Além de resumir as seções chave, inclua uma breve análise sobre a força dos argumentos, a contribuição e as limitações do trabalho."""
        else: # informativo
            instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ser de caráter informativo (cerca de 30% do original), mantendo dados, argumentos e conclusões essenciais."

        return f"""
## INSTRUÇÃO ##
{instrucao_persona}
{instrucao_tarefa}

Com base na sua análise, gere o resumo final seguindo estas duas regras:
1. {instrucao_apresentacao}
2. {instrucao_detalhe}

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

    # CORRIGIDO: Retornar a variável "texto" que contém o input original
    return jsonify({"resumo": response.text, "texto_extraido": texto})


@app.route('/resumir-pdf', methods=['POST'])
def resumir_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({"erro": "Nenhum ficheiro PDF enviado"}), 400

    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify({"erro": "Nenhum ficheiro selecionado"}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            
            texto_extraido = ""
            for page in pdf_document:
                texto_extraido += page.get_text()
            
            pdf_document.close()

            if not texto_extraido.strip():
                # CORRIGIDO: Retornar os dois campos, mesmo em caso de erro
                return jsonify({
                    "resumo": "O PDF parece estar vazio ou contém apenas imagens.",
                    "texto_extraido": ""
                })

            formato = request.form.get("formato")
            detalhe = request.form.get("detalhe")
            
            prompt = montagem_prompt(texto_extraido, formato, detalhe)
            response = model.generate_content(prompt)
            
            # CORRIGIDO: Retornar os dois campos no caminho de sucesso
            return jsonify({"resumo": response.text, "texto_extraido": texto_extraido})

        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
            return jsonify({"erro": "Falha ao ler o ficheiro PDF."}), 500

    return jsonify({"erro": "Formato de ficheiro inválido. Por favor, envie um PDF."}), 400


# if __name__ == '__main__':
#     app.run(debug=True)