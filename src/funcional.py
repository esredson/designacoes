
class Funcional:

    def __init__(self, config):
        self._cargos = config['cargos']
        self._gerar_pessoas(config['pessoas'])
        self._gerar_funcoes(config['funcoes']) 
        self._partes = config['partes']
        self._gerar_colisoes_proibidas(config['colisoes_proibidas'])       

    def _gerar_pessoas(self, config):
        pessoas = {}
        for pessoa in config.keys():
            assert config[pessoa]['cargo'] in self._cargos.keys(), f"Cargo da pessoa ${pessoa} inválido"
            pessoas[pessoa] = {
                'nome': config[pessoa]['nome'],
                'cargo': self._cargos[config[pessoa]['cargo']]
            }
        self._pessoas = pessoas

    def _gerar_funcoes(self, config):
        funcoes = {}
        for funcao in config.keys():
            for pessoa in config[funcao]:
                assert pessoa in self._pessoas.keys(), f"Pessoa ${pessoa} na função ${funcao} inválida"
                funcoes[funcao] = [self._pessoas[pessoa] for pessoa in config[funcao]]
        self._funcoes = funcoes

    def _gerar_colisoes_proibidas(self, config):
        colisoes_proibidas = []
        for i, colisao in enumerate(config):
            parte = colisao['parte']
            assert parte in self._partes.keys(), f"Parte ${parte} na colisão ${i} inválida"
            for funcao in colisao['funcoes']:
                assert funcao in self._funcoes.keys(), f"Função ${funcao} na colisão ${i} inválida"
            colisoes_proibidas.append({
                "parte": self._partes[colisao['parte']],
                "funcao": [self._funcoes[f] for f in colisao['funcoes']]
            })
        self._colisoes_proibidas = colisoes_proibidas

    @property
    def pessoas(self):
        return self._pessoas

    @property
    def funcoes(self):
        return self._funcoes

    @property
    def colisoes_proibidas(self):
        return self._colisoes_proibidas