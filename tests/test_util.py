
import src.util as util

def test_calcular_qualidade_distribuicao_array_tam_igual_ao_de_referencia():
    ref = ['a', 'b', 'c']

    a = ['a', 'b', 'c'] # Sem repetição
    assert util.calcular_qualidade_distribuicao(a, ref) == 1.0

    a = ['a', 'b', 'a'] # Com repetição
    assert util.calcular_qualidade_distribuicao(a, ref) < 1.0



def test_calcular_qualidade_distribuicao_array_tam_multiplo_do_de_referencia():
    ref = ['a', 'b', 'c']

    a = ['a', 'b', 'c', 'a', 'b', 'c'] # Ordem natural
    assert util.calcular_qualidade_distribuicao(a, ref) == 1.0

    # Ordem alternativa 1. É 1.0 pq aproximou os c's mas compensou afastando os b's
    a = ['a', 'b', 'c', 'c', 'b', 'a'] 
    assert util.calcular_qualidade_distribuicao(a, ref) == 1.0

    # Ordem alternativa 2. É menor q 1.0 pq aproximou os b's e c's e não tem como compensar
    a = ['a', 'b', 'b', 'c', 'c', 'a'] 
    assert util.calcular_qualidade_distribuicao(a, ref) < 1.0

    a = ['a', 'b', 'a', 'a', 'b', 'c'] # Com repetição extra
    assert util.calcular_qualidade_distribuicao(a, ref) < 1.0

def test_calcular_qualidade_distribuicao_array_tam_nao_multiplo_do_de_referencia():
    ref = ['a', 'b', 'c']
    
    # Ordem natural repetindo o a
    arr = ['a', 'b', 'c', 'a', 'b', 'c', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) == 1.0

    # Ordem natural repetindo o b. É menor q 1.0 pq o b está mais perto e a repetição é punida
    arr = ['a', 'b', 'c', 'a', 'b', 'c', 'b'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 2ª e 6ª posição. É menor q 1.0 pq, apesar da simetria, aproximou
    # os b's e os c's
    arr = ['a', 'c', 'c', 'a', 'b', 'b', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 2ª e 7ª posição. É menor q 1.0 pq aproximou os a's e os b's
    arr = ['a', 'a', 'c', 'a', 'b', 'c', 'b'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 3ª e 4ª posição. É menor q 1.0 pq aproximou os a's e os c's
    arr = ['a', 'b', 'a', 'c', 'b', 'c', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 3ª e 5ª posição. É menor q 1.0 pq aproximou os b's e os c's
    arr = ['a', 'b', 'b', 'a', 'c', 'c', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 3ª e 7ª posição. É menor q 1.0 pq aproximou os a's e os c's
    arr = ['a', 'b', 'a', 'a', 'b', 'c', 'c']
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 4ª e 5ª posição. É menor que 1.0 pq colocou o a numa posição
    # em q ele fica mais perto do outro a, perdendo a simetria
    arr = ['a', 'b', 'c', 'b', 'a', 'c', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 4ª e 6ª posição. É menor que 1.0 pq, apesar de o b ter ficado
    # na mesma posição, aproximou os dois a's e os dois c's
    arr = ['a', 'b', 'c', 'c', 'b', 'a', 'a']  
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

    # Swap entre 5ª e 6ª posição. É 1.0 pq aproxima os c's mas em compensação afasta os b's
    arr = ['a', 'b', 'c', 'a', 'c', 'b', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) == 1.0

    # Swap entre 5ª e 7ª posição. É 1.0 pq aproximou os a's mas afastou os b's
    a = ['a', 'b', 'c', 'a', 'a', 'c', 'b'] 
    assert util.calcular_qualidade_distribuicao(a, ref) == 1.0

    # Swap entre 6ª e 7ª posição. É 1.0 pq aproximou os a's mas afastou os c's
    arr = ['a', 'b', 'c', 'a', 'b', 'a', 'c'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) == 1.0    

    # Com repetição extra não tem jeito. É menor q 1.0
    arr = ['a', 'b', 'c', 'a', 'b', 'a', 'a'] 
    assert util.calcular_qualidade_distribuicao(arr, ref) < 1.0

def test_calcular_qualidade_distribuicao_array_tam_menor_q_o_de_referencia():
    ref = ['a', 'b', 'c', 'd']
    
    a = ['a', 'b', 'c'] # Sem repetição
    assert util.calcular_qualidade_distribuicao(a, ref) == 1.0

    a = ['a', 'b', 'a'] # Com repetição
    assert util.calcular_qualidade_distribuicao(a, ref) < 1.0
