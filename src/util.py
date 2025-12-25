import datetime, json, re
import numpy as np

def obter_mes_ano_referencia():
    today = datetime.date.today()
    if today.day > 26:
        if today.month == 12:
            return 1, today.year + 1
        else:
            return today.month + 1, today.year
    else:
        return today.month, today.year

def obter_nome_mes(mes):
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    return meses[mes - 1]

def converter_string_para_data(str):
    match = re.match(r"^(\d{1,2})(\/\d{1,2})?(\/\d{2})?$", str)
    if match:
        dia = int(match.group(1))
        
        mes_ref, ano_ref = obter_mes_ano_referencia()

        if match.group(2):
            mes = int(match.group(2).replace('/', ''))
        else:
            mes = mes_ref
            
        if match.group(3):
             ano = int(match.group(3).replace('/', ''))
             ano = ano + 2000 if ano < 2000 else ano
        else:
             ano = ano_ref
             
    return datetime.date(ano, mes, dia)

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


