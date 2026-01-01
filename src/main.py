import util
import os
import pandas as pd
import sys

# Adiciona o diretório src ao path para garantir que imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alocador import Alocador
from gerador_pdf import GeradorPDF
from extratores.extrator_meio_semana_pdf import ExtratorMeioSemanaPdf
from extratores.extrator_fim_semana_jpeg import ExtratorFimSemanaJpeg
from inicializacao import inicializar
from config import Config

# Inicialização centralizada
args, config, mes, ano = inicializar()

# --- Executar Extratores ---
print("Executando extratores...")

# 1. Meio de Semana (PDF)
try:
    ExtratorMeioSemanaPdf(config).executar()
except Exception as e:
    print(f"Erro ao extrair meio de semana: {e}")

# 2. Fim de Semana (JPEG)
try:
    ExtratorFimSemanaJpeg(config).executar()
except Exception as e:
    print(f"Erro ao extrair fim de semana: {e}")

alocador = Alocador(config)
alocador.executar(mes, ano)

gerador = GeradorPDF(config)
gerador.executar()