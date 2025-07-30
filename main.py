import os
from dotenv import load_dotenv
from google import genai

def escolha_texto():
    parametros = input("Que tipo de sumarização você deseja? ")
    texto = input("Qual texto deseja sumarizar? ")
    return parametros, texto

def chamada_api():
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Chave GOOGLE_API_KEY não encontrada. Verifique seu arquivo .env")

    client = genai.Client(api_key=api_key)

    parametros, texto = escolha_texto()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Sumarize o seguinte texto: {texto} usando os seguintes parâmetros: {parametros}"
    )

    print(response.text)

chamada_api()
