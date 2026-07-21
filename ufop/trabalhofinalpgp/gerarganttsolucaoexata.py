import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# 1. Dados extraídos milimetricamente do output do solver (FO = 172)
# Sequência dos Lotes (Variáveis x[j,k])
lotes = ['J03', 'J01', 'J07', 'J10', 'J02', 'J05', 'J13', 'J08', 'J09', 'J11', 
         'J04', 'J14', 'J17', 'J18', 'J06', 'J16', 'J15', 'J12', 'J19', 'J20']

# Tempos de início em cada máquina (Variáveis s[1,k] até s[4,k])
s1 = [0, 1, 3, 8, 9, 12, 14, 18, 20, 24, 27, 31, 32, 34, 38, 41, 46, 49, 51, 54]
s2 = [1, 7, 15, 22, 27, 37, 46, 54, 62, 72, 81, 93, 100, 110, 116, 127, 136, 147, 159, 171]
s3 = [7, 15, 22, 31, 41, 46, 54, 63, 72, 81, 93, 101, 110, 121, 127, 136, 147, 159, 171, 180]
s4 = [11, 22, 27, 34, 46, 53, 59, 67, 81, 87, 101, 105, 117, 125, 133, 141, 155, 166, 180, 185]

# Tempos de Conclusão (Variáveis C[k]) e Atrasos (Variáveis T[k])
C = [12, 24, 31, 36, 49, 56, 61, 68, 84, 88, 103, 106, 118, 128, 135, 143, 158, 170, 182, 186]
T = [0, 0, 0, 0, 0, 0, 1, 0, 18, 4, 7, 2, 4, 0, 15, 7, 38, 26, 50, 0]

# 2. Configuração do Gráfico
fig, ax = plt.subplots(figsize=(16, 10))

# Definindo cores suaves para cada Máquina
cores_maquinas = ['#5DADE2', '#F5B041', '#58D68D', '#AF7AC5']
nomes_maquinas = ['M1 (Misturador)', 'M2 (Forno)', 'M3 (Resfriamento)', 'M4 (Empacotamento)']

# 3. Plotando as barras segmentadas por máquina
for i, lote in enumerate(lotes):
    # Segmento M1: Do início na M1 até o início na M2
    ax.barh(lote, width=s2[i]-s1[i], left=s1[i], color=cores_maquinas[0], edgecolor='black', height=0.6)
    
    # Segmento M2: Do início na M2 até o início na M3 (Onde os gargalos ficam visíveis!)
    ax.barh(lote, width=s3[i]-s2[i], left=s2[i], color=cores_maquinas[1], edgecolor='black', height=0.6)
    
    # Segmento M3: Do início na M3 até o início na M4
    ax.barh(lote, width=s4[i]-s3[i], left=s3[i], color=cores_maquinas[2], edgecolor='black', height=0.6)
    
    # Segmento M4: Do início na M4 até a Conclusão Final (C)
    ax.barh(lote, width=C[i]-s4[i], left=s4[i], color=cores_maquinas[3], edgecolor='black', height=0.6)

    # 4. Adicionando Rótulos
    # Tempo final Cj ao fim da barra (em vermelho se houver atraso)
    cor_texto = '#d62728' if T[i] > 0 else 'black'
    peso = 'bold' if T[i] > 0 else 'normal'
    ax.text(C[i] + 1, i, f"{C[i]}h", va='center', ha='left', color=cor_texto, fontweight=peso, fontsize=10)
    
    # Se o lote atrasou, colocar um aviso à esquerda da barra
    if T[i] > 0:
        ax.text(s1[i] - 2, i, f"[-{T[i]}h]", va='center', ha='right', color='#d62728', fontweight='bold', fontsize=9)

# 5. Ajustes Visuais e Eixos
ax.invert_yaxis() # Para J03 ficar no topo

# Customizando as cores dos nomes dos lotes no eixo Y (Vermelho para os atrasados)
for yTick, atraso in zip(ax.get_yticklabels(), T):
    if atraso > 0:
        yTick.set_color('#d62728')
        yTick.set_fontweight('bold')

ax.set_xlabel('Tempo de Processamento (horas)', fontsize=12, fontweight='bold')
ax.set_ylabel('Lotes', fontsize=12, fontweight='bold')
ax.set_title('Gráfico de Gantt Dinâmico: Flow Shop (4 Máquinas) - Atraso Total: 172h', fontsize=16, fontweight='bold')

ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.set_xticks(range(0, 195, 10))

# 6. Criando Legenda Personalizada
legend_elements = [Patch(facecolor=cores_maquinas[idx], edgecolor='black', label=nomes_maquinas[idx]) for idx in range(4)]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), title="Etapas de Produção")

plt.tight_layout()
plt.show()