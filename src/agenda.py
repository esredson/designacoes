import locale, datetime, util

class Agenda:

    def __init__(self, config):
        dias_semana = config["dias_semana"] 
        self._gerar_datas(dias_semana)

        self._gerar_cancelamentos(config["cancelamentos"])
        
    def _gerar_datas(self, dias_semana):
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')

        mes, ano = util.obter_mes_ano_referencia()

        datas = []

        for dia in range(1, 32):
            try:
                data = datetime.date(ano, mes, dia)
            except ValueError:
                continue
            dia_semana = data.strftime('%A').lower()
            if any(d in dia_semana for d in dias_semana):
                datas.append(data)

        self._datas = datas

    def _gerar_cancelamentos(self, config_cancelamentos):
        cancelamentos = {}
        for str in config_cancelamentos.keys():
            cancelamentos[util.converter_string_para_data(str)] = config_cancelamentos[str]
        for dt in cancelamentos.keys():
            if dt not in self._datas:
                print(f"Data cancelada {dt} não está entre as programadas")
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