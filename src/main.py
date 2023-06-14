
import util
import matplotlib.pyplot as plt
import numpy as np

from agenda import Agenda
from funcional import Funcional
from genetica.genetica import Genetica
from genetica.genetica_adapter import Avaliacao

agenda = Agenda(util.config('agenda'))
funcional = Funcional(util.config('funcional'))
avaliacao = Avaliacao(agenda, funcional)

genetica = Genetica(
    num_genes=len(funcional.funcoes) * len(agenda.datas_validas), 
    valores_possiveis_pros_genes=list(funcional.pessoas.keys()),
    funcao_aptidao=avaliacao.avaliar
)
genetica.executar()





print(genetica.solucao)

unique_values, counts = np.unique(genetica.solucao['cromossomo'], return_counts=True)

for value, count in zip(unique_values, counts):
    print(value, "-", count)

print(genetica.tempo_segundos)

plt.plot(genetica.melhor_aptidao_por_geracao)
plt.show()