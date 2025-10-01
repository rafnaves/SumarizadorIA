import os
from dotenv import load_dotenv
import google.generativeai as genai
import fitz

class ResumidorService:

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def _montagem_prompt(self, texto, formato, detalhe):
        """
        Monta um prompt acadêmico especializado.
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

            return f"{instrucao_persona}\n\n{tarefa_especifica}\n\n{regras}\n\n## TEXTO ORIGINAL ##\n---\n{texto}\n---"
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

            return f"## INSTRUÇÃO ##\n{instrucao_persona}\n{instrucao_tarefa}\n\nCom base na sua análise, gere o resumo final seguindo estas duas regras:\n1. {instrucao_apresentacao}\n2. {instrucao_detalhe}\n\n## TEXTO ORIGINAL ##\n---\n{texto}\n---"

    def gerar_resumo(self, texto, formato, detalhe):
        """
        Gera um resumo a partir de um texto de entrada.
        """
        if not all([texto, formato, detalhe]):
            raise ValueError("Dados incompletos para gerar resumo.")
        
        prompt = self._montagem_prompt(texto, formato, detalhe)
        response = self.model.generate_content(prompt)
        return response.text

    def extrair_texto_pdf(self, pdf_file_stream):
        """
        Extrai o texto de um stream de arquivo PDF.
        """
        try:
            pdf_document = fitz.open(stream=pdf_file_stream.read(), filetype="pdf")
            texto_extraido = ""
            for page in pdf_document:
                texto_extraido += page.get_text()
            pdf_document.close()
            return texto_extraido
        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
            raise IOError("Falha ao ler o ficheiro PDF.")