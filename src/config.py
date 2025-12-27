import json
import os
import glob
import datetime
import locale
import re
import util

class Config:
    def __init__(self, mes, ano, debug=False, diretorio_dados='data'):
        self.mes = mes
        self.ano = ano
        self.debug = debug
        self.diretorio_dados = diretorio_dados
        
        # Carregar config.json
        with open(os.path.join('config', 'config.json'), 'r', encoding='utf-8') as f:
            self._raw_config = json.load(f)
            
        # Inicializar componentes
        self._init_geral()
        self._init_funcional()
        self._init_agenda()
        self._init_designacoes_predefinidas()

    def _init_geral(self):
        config = self._raw_config['geral']
        self._titulo = config['titulo']
        self._subtitulo = config['subtitulo']

    def _init_funcional(self):
        config = self._raw_config['funcional']
        self._pessoas = config['pessoas']
        self._tipos_designacoes_predefinidas = config['tipos_designacoes_predefinidas']
        
        # Gerar funções e validar pessoas
        self._funcoes = config['funcoes']
        for funcao in self._funcoes.keys():
            for pessoa in self._funcoes[funcao]['pessoas']:
                assert pessoa in self._pessoas.keys(), f"Pessoa {pessoa} na função {funcao} inválida"
        
        # Gerar colisões proibidas
        self._colisoes_proibidas = config['colisoes_proibidas']
        for tipo_designacao_predefinida in self._colisoes_proibidas.keys():
            assert tipo_designacao_predefinida in self._tipos_designacoes_predefinidas.keys(), f"Designação predefinida {tipo_designacao_predefinida} na colisão inválida"
            for funcao in self._colisoes_proibidas[tipo_designacao_predefinida]:
                assert funcao in self._funcoes.keys(), f"Função {funcao} na colisão {tipo_designacao_predefinida} inválida"

    def _init_agenda(self):
        config = self._raw_config['agenda']
        dias_semana = config["dias_semana"]
        
        # Gerar datas
        # locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8') # Evitar mudar locale globalmente se possível, mas mantendo lógica original
        try:
            locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
        except:
            pass # Fallback se não tiver o locale

        datas = []
        # Usar self.mes e self.ano em vez de util.obter_mes_ano_referencia
        for dia in range(1, 32):
            try:
                data = datetime.date(self.ano, self.mes, dia)
            except ValueError:
                continue
            dia_semana = data.strftime('%A').lower()
            if any(d in dia_semana for d in dias_semana):
                datas.append(data)
        self._datas = datas

        # Gerar cancelamentos
        config_cancelamentos = config["cancelamentos"]
        cancelamentos = {}
        for str_data in config_cancelamentos.keys():
            # Usar util.converter_string_para_data mas precisamos garantir que ele use o mes/ano corretos
            # O util usa variaveis globais. Vamos setar elas antes ou reimplementar a logica aqui?
            # Melhor setar as globais no util para garantir compatibilidade com o metodo dele
            util.definir_mes_ano_referencia(self.mes, self.ano)
            cancelamentos[util.converter_string_para_data(str_data)] = config_cancelamentos[str_data]
            
        for dt in cancelamentos.keys():
            if dt not in self._datas:
                if self.debug:
                    print(f"Data cancelada {dt} não está entre as programadas")
        self._cancelamentos = cancelamentos

    def _init_designacoes_predefinidas(self):
        padrao_arquivo = f"{self.ano}-{self.mes:02d}-predefinidas*.json"
        caminho_padrao = os.path.join(self.diretorio_dados, padrao_arquivo)

        arquivos_encontrados = glob.glob(caminho_padrao)
        dados_designacoes_predefinidas = {}

        if not arquivos_encontrados:
            if self.debug:
                print(f"AVISO: Nenhum arquivo de designações predefinidas encontrado com o padrão: {caminho_padrao}")
        else:
            for arquivo in arquivos_encontrados:
                if self.debug:
                    print(f"Carregando designações predefinidas de: {arquivo}")
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo_arquivo = json.load(f)
                    if "designacoes_predefinidas" in conteudo_arquivo:
                        dados = conteudo_arquivo["designacoes_predefinidas"]
                        dados_designacoes_predefinidas.update(dados)
                    else:
                        if self.debug:
                            print(f"AVISO: Arquivo {arquivo} não contém a chave 'designacoes_predefinidas'. Ignorando.")
        
        if self.debug:
            print("Conteúdo carregado de Designações Predefinidas:")
            print(json.dumps(dados_designacoes_predefinidas, indent=4, ensure_ascii=False))
            
        # Gerar datas predefinidas
        self._designacoes_predefinidas = {}
        for str_data in dados_designacoes_predefinidas.keys():
            dt = util.converter_string_para_data(str_data)
            self._designacoes_predefinidas[dt] = dados_designacoes_predefinidas[str_data]
            
        for dt in self._designacoes_predefinidas.keys():
            if dt not in self.datas_validas: # Verifica contra datas validas (sem cancelamentos)
                 if self.debug:
                    print(f"Data predefinida {dt} não está entre as programadas")

    # Propriedades Gerais
    @property
    def titulo(self): return self._titulo
    @property
    def subtitulo(self): return self._subtitulo

    # Propriedades Funcional
    @property
    def pessoas(self): return self._pessoas
    @property
    def funcoes(self): return self._funcoes
    @property
    def colisoes_proibidas(self): return self._colisoes_proibidas
    @property
    def tipos_designacoes_predefinidas(self): return self._tipos_designacoes_predefinidas

    # Propriedades Agenda
    @property
    def datas(self): return self._datas
    @property
    def cancelamentos(self): return self._cancelamentos
    @property
    def datas_validas(self):
        dts = self._datas.copy()
        for dt in self.cancelamentos.keys():
            if dt in dts:
                dts.remove(dt)
        return dts

    # Propriedades Designacoes Predefinidas
    @property
    def designacoes_predefinidas(self): return self._designacoes_predefinidas
