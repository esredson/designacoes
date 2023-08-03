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

def calcular_qualidade_distribuicao_antigo(array, valores_referencia):
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
        distancias.append(np.mean(np.diff(indices))) 
    if len(distancias) == 0:
        return 1.0
    return np.mean(distancias)/float(len(valores_referencia))

def calcular_qtd_repeticoes_desnecessarias_antigo(array, valores_referencia):
    valores_permitidos = []
    qtd_repeticoes = 0
    for i, val in enumerate(array):
        if len(valores_permitidos) == 0:
            valores_permitidos = list(valores_referencia)
        if val in valores_permitidos:
            valores_permitidos.remove(val)
        else:
            qtd_repeticoes+=1
    return qtd_repeticoes
        
def find_last(str, array, end_index):
    for i in range(end_index, -1, -1):
        if array[i] == str:
            return i
    return -1

def calcular_qtd_repeticoes_desnecessarias_antigo_2(array, valores_referencia):
    valores_disponiveis = valores_referencia[:]
    qtd_vals_referencia = len(valores_referencia)
    qtd_repeticoes = 0
    for i, val in enumerate(array):
        if len(valores_disponiveis) > 0:
            if val not in valores_disponiveis:
                qtd_repeticoes+=1
            else:
                valores_disponiveis.remove(val)    
        else:
            posicao_anterior = find_last(val, array, end_index=i-1)
            if i - posicao_anterior < qtd_vals_referencia:
                qtd_repeticoes+=1
    return qtd_repeticoes

def calcular_qtd_erros_distribuicao_antigo_com_peso(array, valores_referencia):
    qtd_vals_referencia = len(valores_referencia)
    erro = 0
    for i, val in enumerate(array):
        posicao_anterior = find_last(val, array, end_index=i-1)
        if (posicao_anterior > -1 and (i - posicao_anterior) < qtd_vals_referencia):
            erro+=qtd_vals_referencia-(i-posicao_anterior)
    return erro

def calcular_qtd_erros_distribuicao(array, valores_referencia):
    qtd_vals_referencia = len(valores_referencia)
    qtd_repeticoes = 0
    for i, val in enumerate(array):
        posicao_anterior = find_last(val, array, end_index=i-1)
        if (posicao_anterior > -1 and (i - posicao_anterior) < qtd_vals_referencia):
            qtd_repeticoes+=1
    return qtd_repeticoes

