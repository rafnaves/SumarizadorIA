import os
from dotenv import load_dotenv
from google import genai

def escolha_parametros():
    try:
        escolha = input("Que tipo de sumarização você deseja? 1. Parágrafos, 2. Linha do Tempo, 3. Lista Ordenada: ")
        escolha_int = int(escolha)

        if escolha_int == 1:
            parametros = "Parágrafos"
        elif escolha_int == 2:
            parametros = "Linha do Tempo"
        elif escolha_int == 3:
            parametros = "Lista Ordenada"
        else:
            raise ValueError("Opção inválida. Escolha 1, 2 ou 3.")

        return parametros
    
    except ValueError as e:
        print(f"Erro: {e}")
        return None

def escolha_detalhe():
    try:
        escolha = input("Que nivel de detalhe/tamanho você deseja? 1. Conciso, 2. Médio, 3. Detalhado")
        escolha_int = int(escolha)


        if escolha_int == 1:
            detalhe = "Conciso"
        elif escolha_int == 2:
            detalhe = "Médio"
        elif escolha_int == 3:
            detalhe = "Detalhado"
        else:
            raise ValueError("Opção inválida. Escolha 1, 2 ou 3.")

        return detalhe

    except ValueError as e:
        print(f"Erro: {e}")
        return None
        
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
        instrucao_formato = "- Formato do Resumo: O resumo DEVE ser uma lista ordenada ou de tópicos (bullet points), com os pontos mais importantes no início."

    if detalhe == "Conciso":
        instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ser conciso e direto, contendo apenas os pontos mais cruciais (aproximadamente 2-3 frases ou itens)."
    elif detalhe == "Detalhado":
        instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ser detalhado e abrangente, cobrindo todos os aspectos relevantes do texto original."
    else: # Médio
        instrucao_detalhe = "- Nível de Detalhe: O resumo DEVE ter um equilíbrio entre concisão e profundidade, capturando as ideias principais sem se estender excessivamente."

    # Princípios 8 e 17: Formatar e usar delimitadores para clareza
    prompt_final = f"""
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
    return prompt_final



if __name__ == "__main__":
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Chave GOOGLE_API_KEY não encontrada. Verifique seu arquivo .env")

    client = genai.Client(api_key=api_key)


    texto_para_resumir = input("Cole o texto que você quer resumir: \n")

    parametros = escolha_parametros()
    detalhe = escolha_detalhe()


    if parametros and detalhe:
        prompt_gerado = montagem_prompt(texto_para_resumir, parametros, detalhe)
        
        print("\n--- PROMPT AVANÇADO GERADO ---")
        print(prompt_gerado)


    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_gerado
    )

    print(response.text)