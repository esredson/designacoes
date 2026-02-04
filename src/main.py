import util
import os
import pandas as pd
import sys
import traceback
import datetime

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
try:
    alocador.executar(mes, ano)
except Exception as e:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join("log", f"error_{timestamp}.log")
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    
    print(f"Erro Fatal: {e}")
    print(f"Detalhes do erro foram salvos em: {log_file}")
    sys.exit(1)

gerador = GeradorPDF(config)
gerador.executar()