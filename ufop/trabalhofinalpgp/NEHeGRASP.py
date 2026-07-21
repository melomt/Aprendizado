# Otimização do Sequenciamento - NutriVita Alimentos
# Disciplina: PRO910 - Planejamento e Gestão da Produção
# Abordagem: Heurística NEH Refinada por Meta-heurística GRASP

import random
import copy

def ler_dados_do_arquivo(nome_arquivo):
    """Lê os dados de entrada, incluindo a linha com as datas de entrega (due dates)."""
    try:
        with open(nome_arquivo, 'r') as f:
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
            num_jobs = int(linhas[0])
            num_maquinas = int(linhas[1])
            tempos = []
            
            for i in range(2, 2 + num_jobs):
                tempos.append(list(map(int, linhas[i].split())))
                
            due_dates = list(map(int, linhas[2 + num_jobs].split()))
            return num_jobs, num_maquinas, tempos, due_dates
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return None, None, None, None

def calcular_atraso_total(sequencia, tempos, due_dates):
    """Calcula o atraso total para uma dada sequência de jobs."""
    num_jobs = len(sequencia)
    num_maquinas = len(tempos[0])
    tempo_conclusao = [[0] * num_maquinas for _ in range(num_jobs)]
    
    # Primeiro job
    tempo_conclusao[0][0] = tempos[sequencia[0]][0]
    for m in range(1, num_maquinas):
        tempo_conclusao[0][m] = tempo_conclusao[0][m-1] + tempos[sequencia[0]][m]
        
    # Demais jobs
    for j in range(1, num_jobs):
        tempo_conclusao[j][0] = tempo_conclusao[j-1][0] + tempos[sequencia[j]][0]
        for m in range(1, num_maquinas):
            tempo_conclusao[j][m] = max(tempo_conclusao[j-1][m], tempo_conclusao[j][m-1]) + tempos[sequencia[j]][m]
            
    atraso_total = 0
    for i in range(num_jobs):
        job_idx = sequencia[i]
        c_j = tempo_conclusao[i][-1]
        d_j = due_dates[job_idx]
        atraso_total += max(0, c_j - d_j)
        
    makespan = tempo_conclusao[-1][-1]
    return atraso_total, makespan

def neh_heuristic_atraso(num_jobs, num_maquinas, tempos, due_dates):
    """Heurística NEH original focada em Atraso."""
    jobs_com_dados = [(j, due_dates[j], sum(tempos[j])) for j in range(num_jobs)]
    jobs_com_dados.sort(key=lambda x: (x[1], x[2])) # EDD
    jobs_ordenados = [job for job, _, _ in jobs_com_dados]
    
    sequencia = [jobs_ordenados[0]]
    
    for i in range(1, num_jobs):
        job_a_inserir = jobs_ordenados[i]
        melhor_sequencia = None
        melhor_atraso = float('inf')
        melhor_makespan = float('inf')
        
        for pos in range(i + 1):
            temp_sequencia = sequencia[:pos] + [job_a_inserir] + sequencia[pos:]
            atraso_atual, makespan_atual = calcular_atraso_total(temp_sequencia, tempos, due_dates)
            
            if atraso_atual < melhor_atraso or (atraso_atual == melhor_atraso and makespan_atual < melhor_makespan):
                melhor_atraso = atraso_atual
                melhor_makespan = makespan_atual
                melhor_sequencia = temp_sequencia
                
        sequencia = melhor_sequencia
    return sequencia, melhor_atraso

def busca_local_insercao(sequencia_inicial, tempos, due_dates):
    """Fase de Busca Local do GRASP (Vizinhança por Inserção)."""
    melhor_seq = copy.copy(sequencia_inicial)
    melhor_atraso, melhor_makespan = calcular_atraso_total(melhor_seq, tempos, due_dates)
    
    melhoria = True
    while melhoria:
        melhoria = False
        for i in range(len(melhor_seq)):
            for j in range(len(melhor_seq)):
                if i != j:
                    # Movimento de Inserção: remove da posição i e insere na j
                    seq_vizinha = copy.copy(melhor_seq)
                    job = seq_vizinha.pop(i)
                    seq_vizinha.insert(j, job)
                    
                    atraso_vizinho, makespan_vizinho = calcular_atraso_total(seq_vizinha, tempos, due_dates)
                    
                    # Estratégia First Improvement (Primeira Melhora)
                    if atraso_vizinho < melhor_atraso or (atraso_vizinho == melhor_atraso and makespan_vizinho < melhor_makespan):
                        melhor_seq = seq_vizinha
                        melhor_atraso = atraso_vizinho
                        melhor_makespan = makespan_vizinho
                        melhoria = True
                        break 
            if melhoria:
                break # Reinicia a busca a partir da nova melhor solução
                
    return melhor_seq, melhor_atraso

def construcao_gulosa_aleatorizada(num_jobs, tempos, due_dates, alpha=0.3):
    """Fase de Construção do GRASP utilizando uma RCL."""
    sequencia = []
    candidatos = list(range(num_jobs))
    
    while candidatos:
        custos = []
        for job in candidatos:
            temp_seq = sequencia + [job]
            atraso, makespan = calcular_atraso_total(temp_seq, tempos, due_dates)
            custos.append((job, atraso, makespan))
            
        # Ordena prioritariamente pelo menor atraso
        custos.sort(key=lambda x: (x[1], x[2]))
        
        # Define a Lista Restrita de Candidatos (RCL) com base no fator alpha
        tamanho_rcl = max(1, int(len(candidatos) * alpha))
        rcl = custos[:tamanho_rcl]
        
        # Escolha aleatória dentro da RCL
        job_escolhido = random.choice(rcl)[0]
        sequencia.append(job_escolhido)
        candidatos.remove(job_escolhido)
        
    return sequencia

def executar_metaheuristica_grasp(num_jobs, tempos, due_dates, iteracoes=50, alpha=0.3, seq_neh=None):
    """Loop principal da meta-heurística GRASP."""
    print(f"\n--- Iniciando GRASP ({iteracoes} iterações | Alpha={alpha}) ---")
    
    melhor_solucao_global = None
    melhor_atraso_global = float('inf')
    
    # Passo 1: Refinamento explícito da solução NEH (Semente)
    if seq_neh:
        print(">> Refinando a solução inicial da Heurística NEH...")
        seq_refinada_neh, atraso_refinado_neh = busca_local_insercao(seq_neh, tempos, due_dates)
        melhor_solucao_global = seq_refinada_neh
        melhor_atraso_global = atraso_refinado_neh
        print(f"   Atraso NEH Refinado (Busca Local): {melhor_atraso_global}h")

    # Passo 2: Iterações padrão do GRASP
    print(">> Rodando iterações de Construção + Busca Local do GRASP...")
    for i in range(iteracoes):
        # 1. Construção
        solucao_construida = construcao_gulosa_aleatorizada(num_jobs, tempos, due_dates, alpha)
        
        # 2. Busca Local
        solucao_refinada, atraso_refinado = busca_local_insercao(solucao_construida, tempos, due_dates)
        
        # Atualização da melhor global
        if atraso_refinado < melhor_atraso_global:
            melhor_atraso_global = atraso_refinado
            melhor_solucao_global = solucao_refinada
            print(f"   [Nova Melhor Solução] Iteração {i+1}: Atraso = {melhor_atraso_global}h")
            
    return melhor_solucao_global, melhor_atraso_global

# --- Execução Principal ---
if __name__ == "__main__":
    nome_arquivo = "instancia_1.txt"
    num_jobs, num_maquinas, tempos, due_dates = ler_dados_do_arquivo(nome_arquivo)

    if num_jobs is not None:
        # 1. Roda a Heurística NEH
        print("--- Fase 1: Heurística NEH Construtiva ---")
        seq_neh, atraso_neh = neh_heuristic_atraso(num_jobs, num_maquinas, tempos, due_dates)
        print("Sequência NEH gerada:", [j+1 for j in seq_neh])
        print("Atraso Total NEH:", atraso_neh, "horas")
        
        # 2. Roda a Meta-heurística GRASP (usando a NEH como semente)
        seq_grasp, atraso_grasp = executar_metaheuristica_grasp(
            num_jobs, tempos, due_dates, 
            iteracoes=30, # Você pode aumentar este número para buscar soluções melhores
            alpha=0.3, 
            seq_neh=seq_neh
        )
        
        print("\n=== COMPARAÇÃO DE EXCELÊNCIA (NutriVita) ===")
        print(f"Atraso Total via NEH (Heurística):        {atraso_neh}h")
        print(f"Atraso Total via GRASP (Meta-heurística): {atraso_grasp}h")
        print(f"Ganho / Redução de atraso:                {atraso_neh - atraso_grasp}h")
        print("Melhor Sequência de Lotes (Nomes):       ", [j+1 for j in seq_grasp])