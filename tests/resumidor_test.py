import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app.services.resumidor_service import ResumidorService

if __name__ == "__main__":
    servico_de_teste = ResumidorService()

    texto_exemplo = "O estudo investiga o impacto da fotossíntese. A metodologia utilizada foi a observação. Os resultados indicam uma correlação positiva."

    combinacoes_para_testar = [
        {"formato": "Parágrafos", "detalhe": "critico"},
        {"formato": "Tópicos", "detalhe": "informativo"},
        {"formato": "Extrativo", "detalhe": "indicativo"},
        {"formato": "Extrativo", "detalhe": "critico"} 
    ]

    for i, combo in enumerate(combinacoes_para_testar):
        formato_teste = combo["formato"]
        detalhe_teste = combo["detalhe"]
        
        print(f"\n========== TESTE {i+1}: Formato='{formato_teste}', Detalhe='{detalhe_teste}' ==========")
        
        prompt_gerado = servico_de_teste._montagem_prompt(
            texto=texto_exemplo,
            formato=formato_teste,
            detalhe=detalhe_teste
        )
        
        print(prompt_gerado)
        print(f"========== FIM DO TESTE {i+1} ==========")