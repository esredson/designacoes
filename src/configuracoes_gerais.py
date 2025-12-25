class ConfiguracoesGerais:
    def __init__(self, config):
        self._titulo = config['titulo']
        self._subtitulo = config['subtitulo']

    @property
    def titulo(self):
        return self._titulo

    @property
    def subtitulo(self):
        return self._subtitulo
