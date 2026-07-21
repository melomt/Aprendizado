# Heurística NEH Adaptada para minimizar Atraso Total
# Disciplina: PRO910 - Planejamento e Gestão da Produção
# Baseado no código original do Prof.: Aloisio Gomes Jr.

import matplotlib.pyplot as plt

def ler_dados_do_arquivo(nome_arquivo):
    """Lê os dados de entrada, incluindo a nova linha com as datas de entrega (due dates)."""
    try:
        with open(nome_arquivo, 'r') as f:
            # Filtra linhas vazias
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
            num_jobs = int(linhas[0])
            num_maquinas = int(linhas[1])
            tempos = []
            
            # Lê a matriz de tempos de processamento
            for i in range(2, 2 + num_jobs):
                tempos.append(list(map(int, linhas[i].split())))
                
            # Lê as datas de entrega na última linha
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
    
    # Tempo de conclusão para o primeiro job (lógica original mantida)
    tempo_conclusao[0][0] = tempos[sequencia[0]][0]
    for m in range(1, num_maquinas):
        tempo_conclusao[0][m] = tempo_conclusao[0][m-1] + tempos[sequencia[0]][m]
        
    # Tempo de conclusão para os demais jobs (lógica original mantida)
    for j in range(1, num_jobs):
        tempo_conclusao[j][0] = tempo_conclusao[j-1][0] + tempos[sequencia[j]][0]
        for m in range(1, num_maquinas):
            tempo_conclusao[j][m] = max(tempo_conclusao[j-1][m], tempo_conclusao[j][m-1]) + tempos[sequencia[j]][m]
            
    # Novo: Calcular atraso (Tardiness)
    atraso_total = 0
    for i in range(num_jobs):
        job_idx = sequencia[i]
        c_j = tempo_conclusao[i][-1] # Tempo de conclusão final do job na última máquina
        d_j = due_dates[job_idx]
        atraso = max(0, c_j - d_j)
        atraso_total += atraso
        
    makespan = tempo_conclusao[-1][-1]
    return atraso_total, makespan, tempo_conclusao

def neh_heuristic_atraso(num_jobs, num_maquinas, tempos, due_dates):
    """Implementação da heurística NEH adaptada para atraso."""
    print("--- Início da Heurística NEH Adaptada ---")

    # Passo 1 e 2: Ordenar os jobs via regra EDD (Crescente por due date)
    # Formato: (indice_job, due_date, tempo_total)
    jobs_com_dados = [(j, due_dates[j], sum(tempos[j])) for j in range(num_jobs)]
    
    # Ordena prioritariamente por Due Date, e usa o tempo total (crescente) para desempate
    jobs_com_dados.sort(key=lambda x: (x[1], x[2]))
    jobs_ordenados = [job for job, _, _ in jobs_com_dados]
    
    print("\nPasso 1 e 2: Sequência inicial EDD (Earliest Due Date):")
    print("  ", [j+1 for j in jobs_ordenados])

    # Passo 3: Construir a sequência
    sequencia = [jobs_ordenados[0]]
    print(f"\nPasso 3.1: A sequência inicial é composta pelo Job {jobs_ordenados[0]+1}.")
    
    for i in range(1, num_jobs):
        job_a_inserir = jobs_ordenados[i]
        melhor_sequencia = None
        melhor_atraso = float('inf')
        melhor_makespan = float('inf')
        
        print(f"\nPasso 3.{i+1}: Inserindo o Job {job_a_inserir+1}...")
        
        for pos in range(i + 1):
            temp_sequencia = sequencia[:pos] + [job_a_inserir] + sequencia[pos:]
            atraso_atual, makespan_atual, _ = calcular_atraso_total(temp_sequencia, tempos, due_dates)
            
            # Critério de seleção: menor atraso. Desempate: menor makespan.
            if atraso_atual < melhor_atraso or (atraso_atual == melhor_atraso and makespan_atual < melhor_makespan):
                melhor_atraso = atraso_atual
                melhor_makespan = makespan_atual
                melhor_sequencia = temp_sequencia
                
        sequencia = melhor_sequencia
        print(f"  Melhor posição: {[j+1 for j in sequencia]} -> Atraso: {melhor_atraso} (Makespan: {melhor_makespan})")
    
    print("\n--- Fim da Heurística NEH ---")
    return sequencia

def criar_gantt(sequencia, tempos, due_dates, nome_arquivo):
    """Gera um diagrama de Gantt da solução (adaptado)."""
    num_jobs = len(sequencia)
    num_maquinas = len(tempos[0])
    
    _, makespan, tempo_conclusao = calcular_atraso_total(sequencia, tempos, due_dates)
    
    fig, gnt = plt.subplots(figsize=(15, 8))
    gnt.set_ylim(0, num_maquinas * 10 + 10)
    gnt.set_xlim(0, makespan + 10)
    
    gnt.set_xlabel("Tempo")
    gnt.set_ylabel("Máquinas")
    gnt.set_yticks([5 + 10 * i for i in range(num_maquinas)])
    gnt.set_yticklabels([f"Máquina {i+1}" for i in range(num_maquinas)])
    gnt.grid(True, axis='x')
    
    cores = plt.get_cmap('Pastel1', num_jobs)
    starts = [0] * num_maquinas
    
    for i, job_idx in enumerate(sequencia):
        for m in range(num_maquinas):
            start_time = max(starts[m], tempo_conclusao[i-1][m] if i > 0 else 0)
            if m > 0:
                start_time = max(start_time, tempo_conclusao[i][m-1])
            
            duration = tempos[job_idx][m]
            gnt.broken_barh([(start_time, duration)], (5 + 10 * m - 4, 8), 
                            facecolors=cores(job_idx), edgecolor='black')
            starts[m] = start_time + duration
            gnt.text(start_time + duration / 2, 5 + 10 * m, f"J{job_idx+1}", 
                     ha='center', va='center', color='black', fontweight='bold')
    
    plt.title("Diagrama de Gantt - NEH Adaptada (Atraso)")
    plt.savefig(nome_arquivo)
    print(f"\nDiagrama de Gantt salvo como '{nome_arquivo}'")

# --- Execução Principal ---
if __name__ == "__main__":
    nome_arquivo = "instancia_1.txt"  # Troque para instancia_2.txt para testar a outra
    
    num_jobs, num_maquinas, tempos, due_dates = ler_dados_do_arquivo(nome_arquivo)

    if num_jobs is not None:
        sequencia_final = neh_heuristic_atraso(num_jobs, num_maquinas, tempos, due_dates)
        atraso_final, makespan_final, _ = calcular_atraso_total(sequencia_final, tempos, due_dates)
        
        print("\n--- Resultados Finais ---")
        print("Sequência de Jobs (nomes):", [j+1 for j in sequencia_final])
        print("Atraso Total da solução:", atraso_final)
        print("Makespan gerado:", makespan_final)
        
        criar_gantt(sequencia_final, tempos, due_dates, "gantt_neh_atraso.png")
