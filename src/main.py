import util
import os
import pandas as pd

from funcional import Funcional
from agenda import Agenda
from designacoes_predefinidas import DesignacoesPredefinidas
from alocador import Alocador
from configuracoes_gerais import ConfiguracoesGerais
from gerador_pdf import GeradorPDF

configuracoes_gerais = ConfiguracoesGerais(util.config('geral'))
funcional = Funcional(util.config('funcional'))
agenda = Agenda(util.config('agenda'))
designacoes_predefinidas = DesignacoesPredefinidas(util.config('designacoes_predefinidas'), funcional, agenda)

nome_arquivo_csv = f'designacoes-{util.obter_nome_mes(util.obter_mes_ano_referencia()[0])}-{util.obter_mes_ano_referencia()[1]}.csv'
caminho_arquivo_csv = os.path.join('output', nome_arquivo_csv)
nome_arquivo_pdf = nome_arquivo_csv.replace('.csv', '.pdf')
caminho_arquivo_pdf = os.path.join('output', nome_arquivo_pdf)

df_solucao = None

if os.path.exists(caminho_arquivo_csv):
    print(f"Arquivo {caminho_arquivo_csv} já existe. Pulando alocação e carregando dados.")
    df_solucao = pd.read_csv(caminho_arquivo_csv, index_col=0, header=[0, 1])
else:
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
mes, ano = util.obter_mes_ano_referencia()
gerador = GeradorPDF(configuracoes_gerais, mes, ano)
gerador.gerar(df_solucao, caminho_arquivo_pdf)
print(f"PDF salvo em {caminho_arquivo_pdf}")