import util
import os

from funcional import Funcional
from agenda import Agenda
from designacoes_predefinidas import DesignacoesPredefinidas
from alocador import Alocador

funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))
designacoes_predefinidas = DesignacoesPredefinidas(util.config('designacoes_predefinidas'), funcional, agenda)
alocador = Alocador(funcional, agenda, designacoes_predefinidas)

print("Montando as designações...")
alocador.executar(num_passos=10000)
 
print(alocador.solucao)
print(alocador.score_total)
print(alocador.score_vertical)
print(alocador.score_horizontal)
print(alocador.score_distribuicao)
print(alocador.tempo_execucao)

filename = f'designacoes-{util.obter_nome_mes(util.obter_mes_ano_referencia()[0])}-{util.obter_mes_ano_referencia()[1]}.csv'
filepath = os.path.join('output', filename)
alocador.solucao.to_csv(filepath)
print(f"Solução salva em {filepath}")