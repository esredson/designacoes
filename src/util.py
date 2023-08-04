import datetime, json, re
import numpy as np

def converter_string_para_data(str):
    match = re.match(r"^(\d{1,2})(\/\d{1,2})?(\/\d{2})?$", str)
    if match:
        dia = int(match.group(1))
        mes = int(match.group(2).replace('/', '')) if match.group(2) else datetime.date.today().month
        ano = int(match.group(3).replace('/', '')) if match.group(3) else datetime.date.today().year
    return datetime.date(ano + 2000 if ano < 2000 else ano, mes, dia)

def converter_strings_para_datas(strs):
    dts = []
    for str in strs:
        dts.append(converter_string_para_data(str))
    return dts

def config(prop):
    with open('config\config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config[prop] if prop else config

def remover_primeira_ocorrencia(item, lista):
    index_to_remove = lista.index(item)
    return lista[:index_to_remove] + lista[index_to_remove + 1:]

def find_last(str, array, end_index):
    for i in range(end_index, -1, -1):
        if array[i] == str:
            return i
    return -1

def quantificar_erro_distribuicao(array, valores_referencia):
    qtd_vals_referencia = len(valores_referencia)
    erro = 0
    for i, val in enumerate(array):
        posicao_anterior = find_last(val, array, end_index=i-1)
        if posicao_anterior < 0:
            continue
        distancia_em_relacao_ao_anterior = i - posicao_anterior
        if qtd_vals_referencia - distancia_em_relacao_ao_anterior > 0:
            erro += qtd_vals_referencia - distancia_em_relacao_ao_anterior
    return erro


