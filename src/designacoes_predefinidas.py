import util
import os
import glob
import json

class DesignacoesPredefinidas:

    def __init__(self, mes, ano, funcional, agenda, diretorio_dados='data'):
        self._funcional = funcional
        self._agenda = agenda
        
        dados = self._carregar_dados(mes, ano, diretorio_dados)
        self._gerar_datas(dados)

    def _carregar_dados(self, mes, ano, diretorio_dados):
        nome_mes = util.obter_nome_mes(mes)
        padrao_arquivo = f"designacoes-predefinidas-{nome_mes}-{ano}*.json"
        caminho_padrao = os.path.join(diretorio_dados, padrao_arquivo)

        arquivos_encontrados = glob.glob(caminho_padrao)
        dados_designacoes_predefinidas = {}

        if not arquivos_encontrados:
            print(f"AVISO: Nenhum arquivo de designações predefinidas encontrado com o padrão: {caminho_padrao}")
        else:
            for arquivo in arquivos_encontrados:
                print(f"Carregando designações predefinidas de: {arquivo}")
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo_arquivo = json.load(f)
                    if "designacoes_predefinidas" in conteudo_arquivo:
                        dados = conteudo_arquivo["designacoes_predefinidas"]
                        dados_designacoes_predefinidas.update(dados)
                    else:
                        print(f"AVISO: Arquivo {arquivo} não contém a chave 'designacoes_predefinidas'. Ignorando.")
        
        print("Conteúdo carregado de Designações Predefinidas:")
        print(json.dumps(dados_designacoes_predefinidas, indent=4, ensure_ascii=False))
        
        return dados_designacoes_predefinidas
   
    def _gerar_datas(self, config):
        datas = {}
        for str in config.keys():
            datas[util.converter_string_para_data(str)] = config[str]
        for dt in datas.keys():
            assert dt in self._agenda.datas, f"Data predefinida {dt} não está entre as programadas"
        self._datas = datas
       
    @property
    def datas(self):
        return self._datas
