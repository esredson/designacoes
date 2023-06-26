
import util

from funcional import Funcional
from agenda import Agenda
from extra import Extra
from csp import CSP
#from planilha import Planilha

#from util import *
#result = util.calcular_qtd_repeticoes_desnecessarias(['debora', 'debora', 'debora', 'debora', 'debora', 'debora', 'debora', 'debora'], ['geison', 'debora', 'rafael'])
#result = util.calcular_qtd_repeticoes_desnecessarias(['debora', 'rafael', 'rafael', 'geison', 'geison', 'geison', 'geison', 'debora'], ['geison', 'debora', 'rafael'])
#result = util.calcular_qtd_repeticoes_desnecessarias(['debora', 'rafael', 'geison', 'debora', 'rafael', 'geison', 'debora', 'rafael'], ['geison', 'debora', 'rafael'])

funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))
extra = Extra(util.config('extra'), funcional, agenda)

csp = CSP(funcional, agenda, extra)
csp.qtd_max_repeticoes_por_funcao = 0
csp.executar()
    
print(csp.solucao_formatada)
#planilha = Planilha(csp.solucao_formatada)
#planilha.gerar()
#pdf = planilha.pdf()