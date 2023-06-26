
class Funcional:

    def __init__(self, config):
        self._cargos = config['cargos']
        self._gerar_pessoas(config['pessoas'])
        self._gerar_funcoes(config['funcoes']) 
        self._partes = config['partes']
        self._gerar_colisoes_proibidas(config['colisoes_proibidas'])       

    def _gerar_pessoas(self, config):
        for pessoa in config.keys():
            assert config[pessoa]['cargo'] in self._cargos.keys(), f"Cargo da pessoa {pessoa} inválido"
        self._pessoas = config

    def _gerar_funcoes(self, config):
        for funcao in config.keys():
            for pessoa in config[funcao]['pessoas']:
                assert pessoa in self._pessoas.keys(), f"Pessoa {pessoa} na função {funcao} inválida"
        self._funcoes = config

    def _gerar_colisoes_proibidas(self, config):
        colisoes_proibidas = []
        for parte in config.keys():
            assert parte in self._partes.keys(), f"Parte {parte} na colisão inválida"
            for funcao in config[parte]:
                assert funcao in self._funcoes.keys(), f"Função {funcao} na colisão {parte} inválida"
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