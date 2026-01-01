import util
import os
import pandas as pd
import sys

# Adiciona o diretório src ao path para garantir que imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alocador import Alocador
from gerador_pdf import GeradorPDF
import extratores
from inicializacao import inicializar
from config import Config

# Inicialização centralizada
args, config, mes, ano = inicializar()

# --- Executar Extratores ---
extratores.executar_todos(config)

alocador = Alocador(config)
alocador.executar(mes, ano)

gerador = GeradorPDF(config)
gerador.executar()