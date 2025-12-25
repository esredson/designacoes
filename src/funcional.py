class Funcional:

    def __init__(self, config):
        self._pessoas = config['pessoas']
        self._gerar_funcoes(config['funcoes']) 
        self._tipos_designacoes_predefinidas = config['tipos_designacoes_predefinidas']
        self._gerar_colisoes_proibidas(config['colisoes_proibidas'])       

    def _gerar_funcoes(self, config):
        for funcao in config.keys():
            for pessoa in config[funcao]['pessoas']:
                assert pessoa in self._pessoas.keys(), f"Pessoa {pessoa} na função {funcao} inválida"
        self._funcoes = config

    def _gerar_colisoes_proibidas(self, config):
        colisoes_proibidas = []
        for tipo_designacao_predefinida in config.keys():
            assert tipo_designacao_predefinida in self._tipos_designacoes_predefinidas.keys(), f"Designação predefinida {tipo_designacao_predefinida} na colisão inválida"
            for funcao in config[tipo_designacao_predefinida]:
                assert funcao in self._funcoes.keys(), f"Função {funcao} na colisão {tipo_designacao_predefinida} inválida"
        self._colisoes_proibidas = config

    @property
    def pessoas(self):
        return self._pessoas

    @property
    def funcoes(self):
        return self._funcoes

    @property
    def colisoes_proibidas(self):
        return self._colisoes_proibidas

    @property
    def tipos_designacoes_predefinidas(self):
        return self._tipos_designacoes_predefinidas