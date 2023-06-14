import random, time
import numpy as np

class Genetica:
    
    def __init__(self, num_genes, valores_possiveis_pros_genes, funcao_aptidao):
        self._max_geracoes = 700
        self._tam_populacao = 50
        self._num_genes = num_genes
        self._valores_possiveis_pros_genes = valores_possiveis_pros_genes
        self._funcao_aptidao = funcao_aptidao
        self._solucao = None
        self._melhor_aptidao_por_geracao = []

    def _gerar_cromossomo(self):
        genes = np.array(random.choices(self._valores_possiveis_pros_genes, k=self._num_genes))
        return genes

    def _gerar_individuo(self, cromossomo):
        return {
            'cromossomo': cromossomo,
            'aptidao': self._funcao_aptidao(cromossomo)
        }

    def _gerar_populacao(self):
        return [
            self._gerar_individuo(self._gerar_cromossomo()) 
            for _ in range(self._tam_populacao)
        ]

    def _sortear_pais_aptos_a__reproduzir(self, populacao):
        i_pais = random.choices(
            range(len(populacao)), 
            weights=[individuo['aptidao'] for individuo in populacao], 
            k=2)
        return populacao[i_pais[0]], populacao[i_pais[1]]

    def _causar_mutacao(self, cromossomo):
        # Faz um swap entre dois valores no cromossomo:
        pto1, pto2 = random.sample(range(len(cromossomo)), 2)
        cromossomo[pto1], cromossomo[pto2] = cromossomo[pto2], cromossomo[pto1]

    def _reproduzir(self, pai, mae, mutacao=True):
        # Faz um crossover entre os pais:
        cromo_pai = pai['cromossomo']
        cromo_mae = mae['cromossomo']
        ponto_cruzamento = random.randint(1, len(cromo_pai) - 2)
        cromo_filho1 = np.concatenate((cromo_pai[:ponto_cruzamento], cromo_mae[ponto_cruzamento:]))
        cromo_filho2 = np.concatenate((cromo_mae[:ponto_cruzamento], cromo_pai[ponto_cruzamento:]))
        if (mutacao):
            self._causar_mutacao(cromo_filho1)
            self._causar_mutacao(cromo_filho2)
        return self._gerar_individuo(cromo_filho1), self._gerar_individuo(cromo_filho2)

    def _eliminar_individuo_menos_apto(self, populacao):
        i_menos_apto = min(enumerate(populacao), key=lambda i: i[1]['aptidao'])[0]
        populacao.pop(i_menos_apto)

    def _eliminar_individuos_menos_aptos(self, populacao, n):
        for _ in range(n):
            self._eliminar_individuo_menos_apto(populacao)

    def _selecao_natural(self, populacao):
        pai, mae = self._sortear_pais_aptos_a__reproduzir(populacao)
        filho1, filho2 = self._reproduzir(pai, mae)
        self._eliminar_individuos_menos_aptos(populacao, 2)
        populacao.extend([filho1, filho2])

    def _definir_solucao(self, populacao):
        mais_apto = max(populacao, key=lambda individuo: individuo['aptidao'])
        self._melhor_aptidao_por_geracao.append(mais_apto['aptidao'])
        if self._solucao is None or mais_apto['aptidao'] > self._solucao['aptidao']:
            self._solucao = mais_apto

    def executar(self):
        self._solucao = None
        self._tempo_segundos = 0

        start_time = time.time()

        populacao = self._gerar_populacao()
  
        for geracao in range(self._max_geracoes):
            self._selecao_natural(populacao)
            self._definir_solucao(populacao)

        self._tempo_segundos = time.time() - start_time

    @property
    def solucao(self):
        return self._solucao

    @property
    def tempo_segundos(self):
        return self._tempo_segundos

    @property
    def melhor_aptidao_por_geracao(self):
        return self._melhor_aptidao_por_geracao