
import numpy as np

class GeneticaAdapter:

    def __init__(self, agenda, funcional):
        self._agenda = agenda
        self._funcional = funcional
        self._regras = [self.evitar_repeticoes_mesmo_dia, self.recompensar_boa_distribuicao]

    def recompensar_boa_distribuicao(self, proposta):
        chaves_pessoas = self._funcional.pessoas.keys()
        qtd_por_pessoa = [np.count_nonzero(proposta == nome) for nome in chaves_pessoas]
        media_qtds = np.mean(qtd_por_pessoa)
        std_qtds = np.std(qtd_por_pessoa)
        coeficiente_variacao = (std_qtds/media_qtds)*100
        return 1 - (coeficiente_variacao/100)
    
    def evitar_repeticoes_mesmo_dia(self, proposta):
        qtd_datas_validas = len(self._agenda.datas_validas)
        qtd_funcoes = len(self._funcional.funcoes)
        matriz = proposta.reshape(qtd_datas_validas, qtd_funcoes)
        linhas_por_data = np.split(matriz, matriz.shape[0])
        for linha in linhas_por_data:
            if np.size(np.unique(linha)) != np.size(linha):
                return 0
        return 1    

    def avaliar(self, proposta):
        soma = 0
        for regra in self._regras:
            soma += regra(proposta)
        return soma