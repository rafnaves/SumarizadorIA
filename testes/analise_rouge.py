from rouge_score import rouge_scorer

# --- CONFIGURE AQUI ---
# Para cada obra, coloque o nome dos ficheiros de resumo aqui
# Exemplo para a OBRA 1:
resumo_referencia_file = "/projetollm/testes/vidas_secas/vidassecashumano.txt"
resumos_maquina_files = {
    "Nosso Sistema (Abstrativo)": "/projetollm/testes/vidas_secas/vidassecas_abstrativo.txt",
    "ChatGPT": "/projetollm/testes/vidas_secas/vidassecasgpr.txt",
    "DeepSeek": "/projetollm/testes/vidas_secas/vidassecas_Ds.txt"
}
# --------------------

# Função para ler o conteúdo de um ficheiro
def ler_arquivo(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERRO: Ficheiro não encontrado em '{filepath}'")
        return None

# Carrega o resumo de referência (gabarito)
resumo_referencia = ler_arquivo(resumo_referencia_file)

if resumo_referencia:
    print(f"--- Analisando resumos com base em '{resumo_referencia_file}' ---")
    
    # Configura o calculador ROUGE
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    # Itera sobre cada resumo de máquina para pontuá-lo
    for modelo, arquivo in resumos_maquina_files.items():
        resumo_maquina = ler_arquivo(arquivo)
        if resumo_maquina:
            # Calcula as pontuações comparando com a referência
            scores = scorer.score(resumo_referencia, resumo_maquina)
            
            print(f"\nModelo: {modelo}")
            print(f"  ROUGE-1 F-Score: {scores['rouge1'].fmeasure:.4f}")
            print(f"  ROUGE-2 F-Score: {scores['rouge2'].fmeasure:.4f}")
            print(f"  ROUGE-L F-Score: {scores['rougeL'].fmeasure:.4f}")