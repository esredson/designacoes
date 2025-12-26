import json
import os
import sys
from difflib import get_close_matches

# Adiciona src ao path para importar util se necessário
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
import util

class Conversor:
    def __init__(self, mes, ano, chaves_permitidas=None, debug=False):
        self.mes = mes
        self.ano = ano
        self.debug = debug
        
        # Carregar configurações
        self.config_funcional = util.config('funcional')
        self.pessoas_config = self.config_funcional.get('pessoas', {})
        self.tipos_designacoes = self.config_funcional.get('tipos_designacoes_predefinidas', {})
        
        # Mapeamento reverso: Nome de Exibição -> Chave (ID)
        self.mapa_funcoes = {}
        if chaves_permitidas:
             for chave, dados in self.tipos_designacoes.items():
                if chave in chaves_permitidas:
                    nome_exibicao = dados.get('nome', '').lower()
                    self.mapa_funcoes[nome_exibicao] = chave
        
        # Mapeamento reverso de pessoas: Nome de Exibição -> Chave (ID)
        self.mapa_pessoas = {}
        for chave, dados in self.pessoas_config.items():
            nome_exibicao = dados.get('nome', '').lower()
            self.mapa_pessoas[nome_exibicao] = chave
            
        # Relatório de erros
        self.relatorio_erros = {
            'pessoas_nao_encontradas': set(),
            'funcoes_nao_encontradas': set(),
            'outros_erros': []
        }

    def _log(self, msg):
        if self.debug:
            print(msg)

    def _encontrar_chave_por_nome(self, texto, mapa, tipo_item):
        # Tenta encontrar a chave correspondente ao texto no mapa fornecido
        texto_lower = texto.lower().strip()
        
        if not texto_lower:
            return None
        
        # 1. Tentativa exata
        if texto_lower in mapa:
            return mapa[texto_lower]
            
        for nome_exibicao, chave in mapa.items():
            # 2. Config contido no Texto (Ex: Config="Pedro", Text="Pedro Silva")
            if nome_exibicao in texto_lower:
                return chave
            # 3. Texto contido no Config (Ex: Config="Pedro Silva", Text="Pedro")
            # IMPORTANTE: Apenas se for no início para evitar falsos positivos com sobrenomes (Ex: "Souza" em "Marcelo Souza")
            if nome_exibicao.startswith(texto_lower):
                return chave
        
        # 4. Tentativa fuzzy (difflib) - Cutoff alto para evitar falsos positivos (Ex: Marcelo Souza != João Souza)
        matches = get_close_matches(texto_lower, mapa.keys(), n=1, cutoff=0.8)
        if matches:
            return mapa[matches[0]]
            
        # Se não encontrar
        if tipo_item == 'pessoa':
            self.relatorio_erros['pessoas_nao_encontradas'].add(texto)
        elif tipo_item == 'funcao':
            self.relatorio_erros['funcoes_nao_encontradas'].add(texto)
        elif tipo_item == 'verificacao':
            # Não faz nada, apenas retorna None
            pass
            
        return None

    def salvar_json(self, saida, caminho_json_saida):
        with open(caminho_json_saida, 'w', encoding='utf-8') as f:
            json.dump(saida, f, indent=4, ensure_ascii=False)
        
        print(f"JSON gerado em: {caminho_json_saida}")
        print(json.dumps(saida, indent=4, ensure_ascii=False))

    def exibir_relatorio(self):
        if self.debug or self.relatorio_erros['pessoas_nao_encontradas'] or self.relatorio_erros['funcoes_nao_encontradas'] or self.relatorio_erros['outros_erros']:
            if self.relatorio_erros['pessoas_nao_encontradas']:
                print("\n[!] Pessoas não encontradas no config.json:")
                for p in self.relatorio_erros['pessoas_nao_encontradas']:
                    print(f"    - {p}")
            else:
                if self.debug:
                    print("\n[OK] Todas as pessoas foram encontradas no config.")
                
            if self.relatorio_erros['funcoes_nao_encontradas']:
                print("\n[!] Funções não encontradas no config.json:")
                for f in self.relatorio_erros['funcoes_nao_encontradas']:
                    print(f"    - {f}")
                    
            if self.relatorio_erros['outros_erros']:
                print("\n[!] Outros erros:")
                for e in self.relatorio_erros['outros_erros']:
                    print(f"    - {e}")
                    
            print("\n" + "="*30)
