import util
import os
import pandas as pd
import sys

# Adiciona o diretório src ao path para garantir que imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from designacoes_predefinidas import DesignacoesPredefinidas
from alocador import Alocador
from gerador_pdf import GeradorPDF
from conversores.conversor_meio_semana_pdf import ConversorMeioSemanaPdf
from conversores.conversor_fim_semana_jpeg import ConversorFimSemanaJpeg
from inicializacao import inicializar

# Inicialização centralizada
args, configuracoes_gerais, funcional, agenda, mes, ano = inicializar()

# --- Executar Conversores ---
print("Executando conversores...")

# 1. Meio de Semana (PDF)
try:
    ConversorMeioSemanaPdf(mes, ano, debug=args.debug).executar()
except Exception as e:
    print(f"Erro ao converter meio de semana: {e}")

# 2. Fim de Semana (JPEG)
try:
    ConversorFimSemanaJpeg(mes, ano, debug=args.debug).executar()
except Exception as e:
    print(f"Erro ao converter fim de semana: {e}")

designacoes_predefinidas = DesignacoesPredefinidas(mes, ano, funcional, agenda, debug=args.debug)
alocador = Alocador(funcional, agenda, designacoes_predefinidas, debug=args.debug)

alocador.executar(mes, ano)

gerador = GeradorPDF(configuracoes_gerais, mes, ano, debug=args.debug)
gerador.executar()