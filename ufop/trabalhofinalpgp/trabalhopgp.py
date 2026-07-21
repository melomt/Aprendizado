import time
import random
import matplotlib.pyplot as plt
import numpy as np

# ==============================================================================
# 1. CRIAÇÃO E CARREGAMENTO DE DADOS
# ==============================================================================

CONTEUDO_INSTANCIA = """20
4
3 9 7 3
2 11 8 2
4 5 2 1
3 10 9 3
1 8 5 1
2 9 4 2
2 6 4 1
3 8 4 2
5 12 8 3
1 7 3 1
2 7 5 1
4 10 6 2
2 6 4 1
1 8 3 1
3 12 7 3
2 8 5 2
3 11 6 2
2 10 6 2
4 12 9 3
1 5 3 1
24 50 18 96 60 120 31 70 66 36 84 144 60 104 120 136 114 128 132 192"""

def salvar_instancia_se_necessario(caminho="instancia_1.txt"):
    with open(caminho, "w") as f:
        f.write(CONTEUDO_INSTANCIA)

def carregar_instancia(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    
    num_jobs = int(linhas[0])
    num_maquinas = int(linhas[1])
    
    tempos = []
    for i in range(2, 2 + num_jobs):
        tempos.append(list(map(int, linhas[i].split())))
        
    due_dates = list(map(int, linhas[2 + num_jobs].split()))
    
    return num_jobs, num_maquinas, tempos, due_dates

# ==============================================================================
# 2. AVALIADOR MULTIDIMENSIONAL COMPLETO
# ==============================================================================

def avaliar_completo(sequencia, tempos, due_dates):
    n = len(sequencia)
    m = len(tempos[0])
    
    C = [[0] * m for _ in range(n)]
    S = [[0] * m for _ in range(n)] # Matriz de tempos de início
    
    # Primeiros tempos (posição 0)
    job_0 = sequencia[0]
    S[0][0] = 0
    C[0][0] = tempos[job_0][0]
    for j in range(1, m):
        S[0][j] = C[0][j-1]
        C[0][j] = S[0][j] + tempos[job_0][j]
        
    # Posições subsequentes
    for i in range(1, n):
        job_i = sequencia[i]
        S[i][0] = C[i-1][0]
        C[i][0] = S[i][0] + tempos[job_i][0]
        for j in range(1, m):
            S[i][j] = max(C[i-1][j], C[i][j-1])
            C[i][j] = S[i][j] + tempos[job_i][j]
            
    atraso_total = 0
    adiantamento_total = 0
    jobs_atrasados = 0
    atraso_maximo = 0
    
    detalhes = []
    for i in range(n):
        job_orig = sequencia[i]
        c_j = C[i][-1]
        d_j = due_dates[job_orig]
        t_j = max(0, c_j - d_j)
        e_j = max(0, d_j - c_j)
        
        atraso_total += t_j
        adiantamento_total += e_j
        if t_j > 0:
            jobs_atrasados += 1
        if t_j > atraso_maximo:
            atraso_maximo = t_j
            
        detalhes.append({
            'pos': i + 1,
            'job': job_orig + 1,
            'completion_time': c_j,
            'due_date': d_j,
            'earliness': e_j,
            'tardiness': t_j
        })
        
    makespan = C[-1][-1]
    fo_combinada = atraso_total + adiantamento_total
    
    return {
        'atraso_total': atraso_total,
        'adiantamento_total': adiantamento_total,
        'fo_combinada': fo_combinada,
        'makespan': makespan,
        'jobs_atrasados': jobs_atrasados,
        'perc_atrasados': (jobs_atrasados / n) * 100,
        'atraso_maximo': atraso_maximo,
        'atraso_medio': atraso_total / n,
        'S_matrix': S,
        'C_matrix': C,
        'detalhes': detalhes
    }

# ==============================================================================
# 3. ALGORITMOS (NEH e GRASP)
# ==============================================================================

def resolver_neh(num_jobs, num_maquinas, tempos, due_dates):
    inicio = time.perf_counter()
    jobs_info = [(j, due_dates[j], sum(tempos[j])) for j in range(num_jobs)]
    jobs_info.sort(key=lambda x: (x[1], x[2]))
    jobs_ordenados = [j for j, _, _ in jobs_info]
    
    sequencia = [jobs_ordenados[0]]
    for i in range(1, num_jobs):
        job_atual = jobs_ordenados[i]
        melhor_seq = None
        melhor_atraso = float('inf')
        melhor_makespan = float('inf')
        
        for pos in range(len(sequencia) + 1):
            temp_seq = sequencia[:pos] + [job_atual] + sequencia[pos:]
            res = avaliar_completo(temp_seq, tempos, due_dates)
            atraso, makespan = res['atraso_total'], res['makespan']
            
            if atraso < melhor_atraso or (atraso == melhor_atraso and makespan < melhor_makespan):
                melhor_atraso = atraso
                melhor_makespan = makespan
                melhor_seq = temp_seq
                
        sequencia = melhor_seq
        
    tempo_execucao = time.perf_counter() - inicio
    return sequencia, tempo_execucao

def busca_local_insert(sequencia, tempos, due_dates):
    n = len(sequencia)
    melhor_seq = list(sequencia)
    res = avaliar_completo(melhor_seq, tempos, due_dates)
    melhor_atraso, melhor_ms = res['atraso_total'], res['makespan']
    melhorou = True
    
    while melhorou:
        melhorou = False
        for i in range(n):
            job = melhor_seq.pop(i)
            for j in range(n):
                if i == j:
                    continue
                temp_seq = melhor_seq[:j] + [job] + melhor_seq[j:]
                res_temp = avaliar_completo(temp_seq, tempos, due_dates)
                atraso, ms = res_temp['atraso_total'], res_temp['makespan']
                
                if atraso < melhor_atraso or (atraso == melhor_atraso and ms < melhor_ms):
                    melhor_atraso = atraso
                    melhor_ms = ms
                    melhor_seq = temp_seq
                    melhorou = True
                    break
            if melhorou:
                break
            else:
                melhor_seq.insert(i, job)
                
    return melhor_seq

def construir_solucao_rcl(num_jobs, tempos, due_dates, alpha=0.3):
    candidatos = list(range(num_jobs))
    sequencia = []
    
    while candidatos:
        avaliacoes = []
        for job in candidatos:
            temp_seq = sequencia + [job]
            res = avaliar_completo(temp_seq, tempos, due_dates)
            avaliacoes.append((job, res['atraso_total']))
            
        avaliacoes.sort(key=lambda x: x[1])
        min_cost = avaliacoes[0][1]
        max_cost = avaliacoes[-1][1]
        
        limite = min_cost + alpha * (max_cost - min_cost)
        rcl = [job for job, cost in avaliacoes if cost <= limite]
        
        escolhido = random.choice(rcl)
        sequencia.append(escolhido)
        candidatos.remove(escolhido)
        
    return sequencia

def resolver_grasp(num_jobs, tempos, due_dates, max_iter=30, alpha=0.3, seed=42):
    random.seed(seed)
    inicio = time.perf_counter()
    
    melhor_solucao = None
    melhor_atraso = float('inf')
    
    for it in range(max_iter):
        sol_inicial = construir_solucao_rcl(num_jobs, tempos, due_dates, alpha=alpha)
        sol_refinada = busca_local_insert(sol_inicial, tempos, due_dates)
        res_refinada = avaliar_completo(sol_refinada, tempos, due_dates)
        atraso_refinado = res_refinada['atraso_total']
        
        if atraso_refinado < melhor_atraso:
            melhor_atraso = atraso_refinado
            melhor_solucao = sol_refinada
            
    tempo_execucao = time.perf_counter() - inicio
    return melhor_solucao, tempo_execucao

# ==============================================================================
# 4. GERADOR DE GRÁFICO DE GANTT
# ==============================================================================

def gerar_grafico_gantt(sequencia, tempos, due_dates, titulo, nome_arquivo):
    n = len(sequencia)
    m = len(tempos[0])
    res = avaliar_completo(sequencia, tempos, due_dates)
    S, C = res['S_matrix'], res['C_matrix']
    
    fig, ax = plt.subplots(figsize=(12, 4.5))
    colors = plt.cm.tab20(np.linspace(0, 1, n))
    
    for j in range(m):
        for i in range(n):
            job_id = sequencia[i]
            start = S[i][j]
            duration = tempos[job_id][j]
            
            ax.barh(y=f"Máquina {j+1}", width=duration, left=start, 
                    color=colors[job_id], edgecolor='black', alpha=0.85, height=0.55)
            
            if duration >= 2:
                ax.text(start + duration/2, j, f"J{job_id+1:02d}", 
                        ha='center', va='center', color='black', fontsize=7.5, fontweight='bold')
                
    ax.set_xlabel("Tempo (Horas)", fontsize=10, fontweight='bold')
    ax.set_ylabel("Máquinas", fontsize=10, fontweight='bold')
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300)
    plt.close()
    print(f"✔ Gráfico de Gantt salvo com sucesso: {nome_arquivo}")

# ==============================================================================
# 5. EXECUÇÃO E IMPRESSÃO DOS RELATÓRIOS DO ARTIGO
# ==============================================================================

if __name__ == "__main__":
    ARQUIVO_INSTANCIA = "instancia_1.txt"
    salvar_instancia_se_necessario(ARQUIVO_INSTANCIA)
    n, m, tempos, due_dates = carregar_instancia(ARQUIVO_INSTANCIA)
    
    # 1. GLPK (Sequência Ótima do Modelo exato modelo.out)
    seq_glpk = [2,0,6,9,4,1,12,7,8,10,3,13,16,17,5,15,14,11,18,19] # 0-indexed
    t_glpk = 162.2 # Inserir tempo de execução real obtido no GLPK
    res_glpk = avaliar_completo(seq_glpk, tempos, due_dates)
    
    # 2. NEH
    seq_neh, t_neh = resolver_neh(n, m, tempos, due_dates)
    res_neh = avaliar_completo(seq_neh, tempos, due_dates)
    
    # 3. GRASP
    seq_grasp, t_grasp = resolver_grasp(n, tempos, due_dates)
    res_grasp = avaliar_completo(seq_grasp, tempos, due_dates)
    
    # 4. Geração dos Gráficos de Gantt
    gerar_grafico_gantt(seq_glpk, tempos, due_dates, "Gráfico de Gantt - Solução GLPK (Exata)", "gantt_glpk.png")
    gerar_grafico_gantt(seq_neh, tempos, due_dates, "Gráfico de Gantt - Heurística NEH", "gantt_neh.png")
    gerar_grafico_gantt(seq_grasp, tempos, due_dates, "Gráfico de Gantt - Meta-heurística GRASP", "gantt_grasp.png")
    
    # 5. Relatório Consolidado para o Artigo
    print("\n" + "="*85)
    print("      TABELA COMPARATIVA MULTIDIMENSIONAL PARA A SEÇÃO DE RESULTADOS")
    print("="*85)
    
    fmt = "{:<32} | {:<15} | {:<15} | {:<15}"
    print(fmt.format("Métrica / Indicador", "GLPK (Exato)", "NEH Adaptado", "GRASP (30 iter)"))
    print("-" * 85)
    print(fmt.format("Atraso Total (Sum T_j) [h]", f"{res_glpk['atraso_total']}", f"{res_neh['atraso_total']}", f"{res_grasp['atraso_total']}"))
    print(fmt.format("Adiantamento Total (Sum E_j) [h]", f"{res_glpk['adiantamento_total']}", f"{res_neh['adiantamento_total']}", f"{res_grasp['adiantamento_total']}"))
    print(fmt.format("FO Combinada (Sum T_j + Sum E_j)", f"{res_glpk['fo_combinada']}", f"{res_neh['fo_combinada']}", f"{res_grasp['fo_combinada']}"))
    print(fmt.format("Makespan (C_max) [h]", f"{res_glpk['makespan']}", f"{res_neh['makespan']}", f"{res_grasp['makespan']}"))
    print(fmt.format("Tarefas Atrasadas (N_tardy)", f"{res_glpk['jobs_atrasados']} ({res_glpk['perc_atrasados']:.0f}%)", f"{res_neh['jobs_atrasados']} ({res_neh['perc_atrasados']:.0f}%)", f"{res_grasp['jobs_atrasados']} ({res_grasp['perc_atrasados']:.0f}%)"))
    print(fmt.format("Atraso Máximo (T_max) [h]", f"{res_glpk['atraso_maximo']}", f"{res_neh['atraso_maximo']}", f"{res_grasp['atraso_maximo']}"))
    print(fmt.format("Atraso Médio por Job [h]", f"{res_glpk['atraso_medio']:.2f}", f"{res_neh['atraso_medio']:.2f}", f"{res_grasp['atraso_medio']:.2f}"))
    print(fmt.format("Tempo Computacional (CPU) [s]", f"{t_glpk:.4f}", f"{t_neh:.4f}", f"{t_grasp:.4f}"))
    print("="*85)