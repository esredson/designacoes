
import util

from funcional import Funcional
from agenda import Agenda
from designacoes_predefinidas import DesignacoesPredefinidas
from alocador import Alocador

funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))
designacoes_predefinidas = DesignacoesPredefinidas(util.config('designacoes_predefinidas'), funcional, agenda)

csp = Alocador(funcional, agenda, designacoes_predefinidas)
csp.executar(num_passos=10000)
 
print(csp.solucao)
print(csp.score_total)
print(csp.score_vertical)
print(csp.score_horizontal)
print(csp.score_distribuicao)
print(csp.tempo_execucao) 
