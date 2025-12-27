import argparse
import util
from funcional import Funcional
from agenda import Agenda
from configuracoes_gerais import ConfiguracoesGerais

def inicializar(descricao="Gerador de Designações", parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description=descricao)
    
    parser.add_argument('--mes', type=int, help='Mês de referência (1-12)')
    parser.add_argument('--ano', type=int, help='Ano de referência (ex: 2025)')
    parser.add_argument('--debug', action='store_true', help='Ativa modo debug')
    
    args = parser.parse_args()
    
    util.definir_mes_ano_referencia(args.mes, args.ano)
    
    configuracoes_gerais = ConfiguracoesGerais(util.config('geral'))
    funcional = Funcional(util.config('funcional'))
    agenda = Agenda(util.config('agenda'))
    
    mes, ano = util.obter_mes_ano_referencia()
    
    return args, configuracoes_gerais, funcional, agenda, mes, ano
