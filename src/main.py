
import util

from funcional import Funcional
from agenda import Agenda
from extra import Extra
from alocador import Alocador

funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))
extra = Extra(util.config('extra'), funcional, agenda)

csp = Alocador(funcional, agenda, extra)
csp.executar(num_passos=10000)
 
print(csp.solucao)
print(csp.error_score)    
print(csp.tempo_execucao) 
