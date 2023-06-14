import datetime, json, re
import numpy as np

def converter_string_para_data(str):
    match = re.match(r"^(\d{1,2})(\/\d{1,2})?(\/\d{2})?$", str)
    if match:
        dia = int(match.group(1))
        mes = int(match.group(2).replace('/', '')) if match.group(2) else datetime.date.today().month
        ano = int(match.group(3).replace('/', '')) if match.group(3) else datetime.date.today().year
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

def calcular_qualidade_distribuicao(array, valores_referencia):
    """
    Calcula o quão bem os valores de referência estão distribuídos no array. \
    O ideal é que nenhum desses valores se repita no array. Mas, quando o \
    array é maior que o número de valores de referência, isso não é possível. \
    Então, havendo valores repetidos, o ideal é que eles estejam distantes \
    entre si o máximo possível, ou seja, que a distância média entre as repetições \
    seja igual ao número de valores de referência, de modo que cada valor só \
    se repita quando todos os outros já tiverem aparecido. 
    """
    distancias = []

    for ref_val in valores_referencia:
        indices = [i for i, val in enumerate(array) if val == ref_val]
        if len(indices) < 2:
            continue
        distancias.append(min(np.diff(indices))) 
    if len(distancias) == 0:
        return 1.0
    return np.mean(distancias)/float(len(valores_referencia))
