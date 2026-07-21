import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# 1. Nova sequência otimizada pelo GRASP
lotes = [
    'J03', 'J01', 'J07', 'J10', 'J05', 'J13', 'J02', 'J09', 'J08', 'J14', 
    'J11', 'J04', 'J06', 'J15', 'J17', 'J19', 'J18', 'J16', 'J12', 'J20'
]

# 2. Duração de cada lote (extraída dos seus dados da primeira tabela)
duracoes_dict = {
    'J01': 12, 'J02': 13, 'J03': 12, 'J04': 15, 'J05': 7,
    'J06': 7,  'J07': 7,  'J08': 7,  'J09': 16, 'J10': 5,
    'J11': 4,  'J12': 12, 'J13': 5,  'J14': 3,  'J15': 15,
    'J16': 8,  'J17': 12, 'J18': 10, 'J19': 12, 'J20': 4
}

# 3. Calculando dinamicamente os novos tempos de Início e Fim (Cj)
inicios = []
fins = []
duracoes = []
tempo_atual = 0

for lote in lotes:
    duracao = duracoes_dict[lote]
    inicios.append(tempo_atual)
    tempo_atual += duracao
    fins.append(tempo_atual)
    duracoes.append(duracao)

# 4. Identificador de atraso (Como o atraso total caiu para apenas 7h, coloquei todos no prazo)
# ATENÇÃO: Se você souber qual lote atrasou, mude o 'False' correspondente para 'True' nesta lista!
atrasados = [False] * 20 

# Definindo cores (Verde para No Prazo, Vermelho para Atrasado)
cor_no_prazo = '#2ca02c'
cor_atrasado = '#d62728'
cores = [cor_atrasado if atraso else cor_no_prazo for atraso in atrasados]

# 5. Configuração do Gráfico
fig, ax = plt.subplots(figsize=(14, 8))

# Criando as barras horizontais
bars = ax.barh(lotes, width=duracoes, left=inicios, color=cores, edgecolor='black', height=0.6)

# Inverter o eixo Y para o primeiro lote (J03) aparecer no topo
ax.invert_yaxis()

# Configuração dos eixos
ax.set_xlabel('Tempo de Processamento Acumulado (horas)', fontsize=12, fontweight='bold')
ax.set_ylabel('Lotes (Nova Sequência GRASP)', fontsize=12, fontweight='bold')
ax.set_title('Gráfico de Gantt - Solução GRASP (Atraso: 7h)', fontsize=16, fontweight='bold')

# Adicionando linhas de grade
ax.grid(axis='x', linestyle='--', alpha=0.7)
ax.set_xticks(range(0, 190, 10))

# 6. Adicionando rótulos de tempo (Cj) no final das barras
for i, bar in enumerate(bars):
    ax.text(
        bar.get_x() + bar.get_width() + 1, 
        bar.get_y() + bar.get_height()/2, 
        f"{fins[i]}h", 
        va='center', 
        ha='left', 
        fontsize=9,
        color='black'
    )

# 7. Criando a Legenda personalizada
legend_elements = [
    Patch(facecolor=cor_no_prazo, edgecolor='black', label='No Prazo'),
    Patch(facecolor=cor_atrasado, edgecolor='black', label='Atrasado')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=12)

# Ajuste de layout e exibição
plt.tight_layout()
plt.show()