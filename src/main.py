import util
import os
import pandas as pd
import sys

# Adiciona o diretório src ao path para garantir que imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alocador import Alocador
from gerador_pdf import GeradorPDF
from conversores.conversor_meio_semana_pdf import ConversorMeioSemanaPdf
from conversores.conversor_fim_semana_jpeg import ConversorFimSemanaJpeg
from inicializacao import inicializar

# Inicialização centralizada
args, config, mes, ano = inicializar()

# --- Executar Conversores ---
print("Executando conversores...")

# 1. Meio de Semana (PDF)
try:
    ConversorMeioSemanaPdf(config).executar()
except Exception as e:
    print(f"Erro ao converter meio de semana: {e}")

# 2. Fim de Semana (JPEG)
try:
    ConversorFimSemanaJpeg(config).executar()
except Exception as e:
    print(f"Erro ao converter fim de semana: {e}")

alocador = Alocador(config)
alocador.executar(mes, ano)

gerador = GeradorPDF(config)
gerador.executar()