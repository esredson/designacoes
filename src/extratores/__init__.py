import pkgutil
import importlib
import inspect
import os
from .extrator import Extrator

def executar_todos(config):
    """
    Carrega e executa dinamicamente todos os extratores encontrados neste pacote.
    """
    package_dir = os.path.dirname(__file__)
    package_name = __name__

    # print(f"Procurando extratores em: {package_dir}")

    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        # Ignora o próprio arquivo __init__ e o módulo base se necessário (embora a lógica de classe cuide disso)
        if module_name == "extrator":
            continue

        # print(f"Verificando módulo: {module_name}")
        try:
            # Importa o módulo
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)
            
            # Procura por classes que herdam de Extrator
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # print(f"  Classe encontrada: {name}")
                if issubclass(obj, Extrator) and obj is not Extrator:
                    # Verifica se a classe foi definida neste módulo (evita duplicatas de imports)
                    if obj.__module__ == full_module_name:
                        print(f"Executando extrator: {name}...")
                        try:
                            extrator = obj(config)
                            extrator.executar()
                        except Exception as e:
                            print(f"Erro ao executar {name}: {e}")
                    # else:
                    #     print(f"  Ignorando {name} (definido em {obj.__module__})")
        except Exception as e:
            print(f"Erro ao carregar módulo {module_name}: {e}")
