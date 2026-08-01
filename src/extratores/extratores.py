import os
import sys

# Garante que o diretório src (e não o diretório deste arquivo) seja o primeiro
# no path, para que "extratores" resolva para o pacote e não para este próprio módulo
# (necessário tanto ao rodar este arquivo diretamente quanto ao importá-lo como parte do pacote).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pkgutil
import importlib
import inspect

from extratores.extrator import Extrator

def executar_todos(config):
    package_dir = os.path.dirname(__file__)
    package_name = "extratores"

    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        if module_name in ("extrator", "extratores"):
            continue

        try:
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Extrator) and obj is not Extrator:
                    if obj.__module__ == full_module_name:
                        print(f"Executando extrator: {name}...")
                        try:
                            extrator = obj(config)
                            extrator.executar()
                        except Exception as e:
                            print(f"Erro ao executar {name}: {e}")
        except Exception as e:
            print(f"Erro ao carregar módulo {module_name}: {e}")

if __name__ == "__main__":
    from inicializacao import inicializar

    try:
        args, config, mes, ano = inicializar(descricao='Executa todos os extratores disponíveis')

        executar_todos(config)

    except Exception as e:
        print(f"Erro fatal: {str(e)}")
        sys.exit(1)
