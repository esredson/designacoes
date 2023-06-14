import locale, datetime, util

class Agenda:

    def __init__(self, config):
        dias_semana = config["dias_semana"] 
        self._gerar_datas(dias_semana)

        datas_extras = util.converter_strings_para_datas(config["datas_extras"])
        self._incluir_datas_extras(datas_extras)

        self._gerar_cancelamentos(config["cancelamentos"])
        
    def _gerar_datas(self, dias_semana):
        locale.setlocale(locale.LC_TIME, 'pt_PT.utf8')

        ano = datetime.date.today().year
        mes = datetime.date.today().month

        datas = []

        for dia in range(1, 32):
            try:
                data = datetime.date(ano, mes, dia)
            except ValueError:
                continue
            dia_semana = data.strftime('%a').lower()
            if dia_semana in dias_semana:
                datas.append(data)

        self._datas = datas

    def _incluir_datas_extras(self, datas_extras):
        for dt in datas_extras:
            assert not dt in self._datas, f"Data extra ${dt} já consta entre as datas programadas"
        for dt in datas_extras:
            self._datas.append(dt)
        self._datas.sort

    def _gerar_cancelamentos(self, config_cancelamentos):
        cancelamentos = {}
        for str in config_cancelamentos.keys():
            cancelamentos[util.converter_string_para_data(str)] = config_cancelamentos[str]
        for dt in cancelamentos.keys():
            assert dt in self._datas, f"Data cancelada ${dt} não está entre as programadas"
        self._cancelamentos = cancelamentos

    @property
    def datas(self):
        return self._datas

    @property
    def cancelamentos(self):
        return self._cancelamentos

    @property
    def datas_validas(self):
        dts = self._datas.copy()
        for dt in self.cancelamentos.keys():
            dts.remove(dt)
        return dts
