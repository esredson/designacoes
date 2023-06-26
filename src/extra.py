import util

class Extra:

    def __init__(self, config, funcional, agenda):
        self._funcional = funcional
        self._agenda = agenda
        self._gerar_datas(config)
   
    def _gerar_datas(self, config):
        datas = {}
        for str in config.keys():
            datas[util.converter_string_para_data(str)] = config[str]
        for dt in datas.keys():
            assert dt in self._agenda.datas, f"Data extra {str} não está entre as programadas"
        self._datas = datas
       
    @property
    def datas(self):
        return self._datas