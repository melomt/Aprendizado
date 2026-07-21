# Problema de Flow Shop 
# Data: 23/01/2024
# Baseado no Modelo Apresentado no Livro Pesquisa Operacional (Arenales et al., 2008)

# --------------- Declara��o dos Par�metros Iniciais -----------------------
param m; # n�mero de m�quinas
param n; # n�mero de jobs


# --------------------- Declara��o dos Conjuntos ---------------------------
set N := 1..n; # conjunto de tarefas (jobs)
set M := 1..m; # conjunto de m�quinas


# --------------------- Declara��o dos Par�metros ---------------------------
param p{i in N, k in M}; # tempo de processamento do job 'i' na m�quina 'k'

param d{i in N}; # data desejada de entrega do job 'i'

# --------------------- Declara��o das vari�veis ---------------------------

var s{k in M, j in N}, >=0; 
# instante de in�cio de processamento na posi��o 'j' na m�quina 'k'.

var x{i in N, j in N}, binary;
# = 1 se a tarefa 'i' � designada a posi��o 'j', =0 c.c.

var C{j in N}, >= 0;
# Data de conclus�o da tarefa na posi��o 'j'

var T{j in N}, >=0;
# Atraso da tarefa na posi��o 'j'


var E{j in N}, >=0;

# Antecipacao da tarefa na posi��o 'j'


# ------------------------- Fun��o Objetivo --------------------------------

# Minimizar o tempo total de execu��o de todas as tarefas (jobs)
# minimize FO: s[m,n] + sum{i in N} p[i,m]*x[i,n];
# Minimizar o tempo total de fluxo
# minimize FO: sum{j in N}C[j];
# Minimizar o atraso total
 minimize FO: sum{j in N}(T[j]+E[j]);

# ---------------------- Restri��es do Problema ----------------------------

# cada tarefa 'i' est� associada a uma �nica posi��o
s.t. r02{i in N}: sum{j in N} x[i,j] = 1;

# asseguram que cada posi��o 'j' esta associada a uma �nica tarefa
s.t. r03{j in N}: sum{i in N} x[i,j] = 1; 

# For�am a tarefa na posi�ao 'j' a iniciar o seu processamento na m�quina 1
# depois que sua tarefa predecessora tenha sido processados nesta m�quina
s.t. r04{j in 1..(n-1)}: s[1,j] + sum{i in N} p[i,1]*x[i,j] = s[1,j+1]; 

# Estabelece que a primeira tarefa da sequencia comece seu processamento na m�quina 1
# no instante 0
s.t. r05: s[1,1] = 0;

# Garante que a primeira tarefa na sequencia seja processada imediatamente na pr�xima 
# m�quina 'k+1', desde que seu processamento na maquina correspondente 'k' tenha sido
# completado
s.t. r06{k in 1..(m-1)}: s[k,1] + sum{i in N} p[i,k]*x[i,1] = s[k+1, 1];

# Asseguaram que uma tarefa na posicao 'j' nao pode ser iniciada na proxima m�quina 'k+1'
# antes do t�rmino do seu processamento na m�quina correspondente 'k'.
s.t. r07{j in 2..n, k in 1..(m-1)}: s[k,j] + sum{i in N} p[i,k]*x[i,j] <= s[k+1, j];

# Garantem que uma tarefa na posicao 'j+1' nao pode iniciar em uma m�quina 'k' antes
# que o processamento da tarefa na posicao 'j' na mesma m�quina 'k' tenha sido completado.
s.t. r08{j in 1..(n-1), k in 2..m}: s[k,j] + sum{i in N} p[i,k]*x[i,j] <= s[k, j+1];

# Definem a data de conclus�o de cada tarefa alocada na posi��o 'j'
s.t. r12{j in N}: C[j] = s[m,j] + sum{i in N}p[i,m]*x[i,j];

# Definem o valor do atraso de cada tarefa alocada na posi��o 'j'
s.t. r13{j in N}: T[j] >= C[j] - sum{i in N}d[i]*x[i,j];


# Definem o valor do atraso de cada tarefa alocada na posi��o 'j'
s.t. r17{j in N}: E[j] >= 0;


end;
