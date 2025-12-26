import util
import os
import pandas as pd
import argparse

from funcional import Funcional
from agenda import Agenda
from designacoes_predefinidas import DesignacoesPredefinidas
from alocador import Alocador
from configuracoes_gerais import ConfiguracoesGerais
from gerador_pdf import GeradorPDF

# Configuração de argumentos da linha de comando
parser = argparse.ArgumentParser(description='Gerador de Designações')
parser.add_argument('--mes', type=int, help='Mês de referência (1-12)')
parser.add_argument('--ano', type=int, help='Ano de referência (ex: 2025)')
args = parser.parse_args()

# Define mês e ano de referência
util.definir_mes_ano_referencia(args.mes, args.ano)

configuracoes_gerais = ConfiguracoesGerais(util.config('geral'))
funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))

mes, ano = util.obter_mes_ano_referencia()

nome_arquivo_csv = f'{ano}-{mes:02d}-designacoes.csv'
caminho_arquivo_csv = os.path.join('data', nome_arquivo_csv)
nome_arquivo_pdf = nome_arquivo_csv.replace('.csv', '.pdf')
caminho_arquivo_pdf = os.path.join('data', nome_arquivo_pdf)

df_solucao = None

if os.path.exists(caminho_arquivo_csv):
    print(f"Arquivo {caminho_arquivo_csv} já existe. Pulando alocação e carregando dados.")
    df_solucao = pd.read_csv(caminho_arquivo_csv, index_col=0, header=[0, 1])
else:
    designacoes_predefinidas = DesignacoesPredefinidas(mes, ano, funcional, agenda)
    alocador = Alocador(funcional, agenda, designacoes_predefinidas)

    print("Montando as designações...")
    alocador.executar()
    
    print(alocador.solucao)
    print(alocador.score_total)
    print(alocador.score_vertical)
    print(alocador.score_horizontal)
    print(alocador.score_distribuicao)
    print(f"Tempo de execução: {alocador.tempo_execucao:.2f} segundos")

    df_solucao = alocador.solucao
    df_solucao.to_csv(caminho_arquivo_csv)
    print(f"Solução salva em {caminho_arquivo_csv}")

print("Gerando PDF...")
gerador = GeradorPDF(configuracoes_gerais, mes, ano)
gerador.gerar(df_solucao, caminho_arquivo_pdf)
print(f"PDF salvo em {caminho_arquivo_pdf}")