
import util

from funcional import Funcional
from agenda import Agenda
from extra import Extra
from csp import CSP

funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))
extra = Extra(util.config('extra'), funcional, agenda)

csp = CSP(funcional, agenda, extra)
csp.qtd_max_repeticoes_por_funcao = 2
csp.executar()
    
print(csp.solucao_formatada)
