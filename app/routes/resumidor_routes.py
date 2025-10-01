from flask import Blueprint, request, jsonify, render_template
from app.services import resumidor_service
from app.services.resumidor_service import ResumidorService
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import fitz


resumidor_bp = Blueprint('resumidor', __name__)

try:
    resumidor_service = ResumidorService()
except ValueError as e:
    print(f"ERRO DE CONFIGURAÇÃO NO BLUEPRINT: {e}")
    resumidor_service = None


@resumidor_bp.route("/")
def index():
    return render_template("index.html")

@resumidor_bp.route('/resumir', methods=['POST'])
def resumir():
    data = request.json
    texto = data.get("texto")
    formato = data.get("formato")
    detalhe = data.get("detalhe")

    if not all([texto, formato, detalhe]):
        return jsonify({"erro": "Dados incompletos"}), 400

    resumo_gerado = resumidor_service.gerar_resumo(texto, formato, detalhe)
    return jsonify({"resumo": resumo_gerado, "texto_extraido": texto})

    # CORRIGIDO: Retornar a variável "texto" que contém o input original
    return jsonify({"resumo": response.text, "texto_extraido": texto})

@resumidor_bp.route('/resumir-pdf', methods=['POST'])
def resumir_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({"erro": "Nenhum ficheiro PDF enviado"}), 400

    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify({"erro": "Nenhum ficheiro selecionado"}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # GARANTA que você está usando a variável 'resumidor_service' (com 's' minúsculo)
            texto_extraido = resumidor_service.extrair_texto_pdf(file.stream)

            if not texto_extraido.strip():
                return jsonify({
                    "resumo": "O PDF parece estar vazio ou contém apenas imagens.",
                    "texto_extraido": ""
                })

            formato = request.form.get("formato")
            detalhe = request.form.get("detalhe")

            # GARANTA que a chamada aqui também usa a instância 'resumidor_service'
            resumo_gerado = resumidor_service.gerar_resumo(texto_extraido, formato, detalhe)

            return jsonify({"resumo": resumo_gerado, "texto_extraido": texto_extraido})

        except IOError as e:
            return jsonify({"erro": str(e)}), 500
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception as e:
            # A mensagem de erro que você viu no log provavelmente foi impressa por esta linha
            print(f"Erro ao processar PDF: {e}")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500