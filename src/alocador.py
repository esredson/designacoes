import pandas as pd
import random
import time
import util
import numpy as np

#from tqdm import tqdm

class Alocador:

    def __init__(self, funcional, agenda, extra):
        self._funcional = funcional
        self._agenda = agenda
        self._extra = extra
        self._solucao = None
        self._score_total = None
        self._score_vertical = None
        self._score_horizontal = None
        self._tempo_execucao = None

    def executar(self, num_passos=1000, peso_vertical=1.0, peso_horizontal=1.0):
        melhor_solucao = None
        melhor_score_total = float('inf')
        melhor_score_vertical = float('inf')
        melhor_score_horizontal = float('inf')

        inicio = time.time()
        
        for _ in range(num_passos):
            solucao = self._alocar()
            
            # Scores (quanto menor, melhor)
            score_vertical = self._quantificar_variancia_vertical(solucao)
            score_horizontal = self._quantificar_variancia_horizontal(solucao)
            
            score_total = (score_vertical * peso_vertical) + (score_horizontal * peso_horizontal)

            if melhor_solucao is None or score_total < melhor_score_total:
                melhor_solucao = solucao
                melhor_score_total = score_total
                melhor_score_vertical = score_vertical
                melhor_score_horizontal = score_horizontal

        self._solucao = melhor_solucao
        self._score_total = melhor_score_total
        self._score_vertical = melhor_score_vertical
        self._score_horizontal = melhor_score_horizontal
        self._tempo_execucao = time.time() - inicio

        self._solucao = self._solucao.applymap(lambda v: self._funcional.pessoas[v]['nome'])

    def _alocar(self):
        df = pd.DataFrame(
            columns=self._funcional.funcoes.keys(), 
            index=self._agenda.datas_validas
        )

        # Coloca as funções em ordem de núm. de pessoas disponíveis, pra iniciar a alocação pela função mais restrita:
        funcoes_ordem_num_pessoas_asc = sorted(self._funcional.funcoes.keys(), key=lambda funcao: len(self._funcional.funcoes[funcao]['pessoas']))

        for funcao in funcoes_ordem_num_pessoas_asc:
            self._alocar_pessoas_para_funcao(funcao, df)

        return df

    def _alocar_pessoas_para_funcao(self, funcao, df):
        pessoas_da_funcao=self._funcional.funcoes[funcao]['pessoas']
        random.shuffle(pessoas_da_funcao)
        fila_pessoas_para_alocacao = pessoas_da_funcao.copy()
        for dt in self._agenda.datas_validas:
            pessoa = self._obter_proxima_pessoa_da_fila(fila_pessoas_para_alocacao, funcao, dt, df)
            if pessoa is None:
                fila_pessoas_para_alocacao += pessoas_da_funcao # Esgotou o pool de pessoas disponíveis? Repete o pool
                pessoa = self._obter_proxima_pessoa_da_fila(fila_pessoas_para_alocacao, funcao, dt, df)
            if pessoa is None:
                raise "Não há pessoas disponíveis para a função"
            df.at[dt, funcao] = pessoa

            fila_pessoas_para_alocacao = util.remover_primeira_ocorrencia(pessoa, fila_pessoas_para_alocacao)

    def _obter_proxima_pessoa_da_fila(self, fila_pessoas_para_alocacao, funcao, dt, df):
        return next((p for p in fila_pessoas_para_alocacao if (
            not self._pessoa_ja_estah_alocada_na_data(p, dt, df) 
            and not self._pessoa_estah_impedida_para_a_funcao_na_data(p, funcao, dt)
        )), None)

    def _pessoa_ja_estah_alocada_na_data(self, pessoa, dt, df):
        return pessoa in df.loc[dt].values
    
    def _pessoa_estah_impedida_para_a_funcao_na_data(self, pessoa, funcao, dt):
        for x in self._extra.datas[dt]:
            if (
                x['parte'] in self._funcional.colisoes_proibidas.keys() 
                and funcao in self._funcional.colisoes_proibidas[x['parte']] 
                and x['pessoa'] == pessoa
            ):
                return True

    def _quantificar_variancia_vertical(self, df):
        scores = []
        for pessoa in self._funcional.pessoas.keys():
            rows, _ = np.where(df.values == pessoa)
            rows = np.sort(rows)
            
            if len(rows) < 2:
                scores.append(0)
                continue
            
            intervalos = np.diff(rows)
            # Soma do inverso dos intervalos (penaliza intervalos pequenos, ex: dias consecutivos)
            scores.append(np.sum(1.0 / intervalos))
            
        return np.mean(scores) if scores else 0

    def _quantificar_variancia_horizontal(self, df):
        variancias = []
        for pessoa in self._funcional.pessoas.keys():
            funcoes_eligible = [f for f, data in self._funcional.funcoes.items() if pessoa in data['pessoas']]
            
            if not funcoes_eligible:
                continue
                
            counts = []
            for f in funcoes_eligible:
                count = (df[f] == pessoa).sum()
                counts.append(count)
            
            # Variância dos counts (penaliza desequilíbrio entre funções)
            variancias.append(np.var(counts))
            
        return np.mean(variancias) if variancias else 0
            
    def _quantificar_erro_distribuicao_por_funcao(self, df):
        erro = 0
        for funcao, pessoas_alocadas in df.items():
            erro += util.quantificar_erro_distribuicao(pessoas_alocadas.values, self._funcional.funcoes[funcao]['pessoas'])
        return erro

    def _quantificar_erro_distribuicao_geral(self, df):
        qtd_alocacoes_por_pessoa = pd.Series(df.values.flatten()).value_counts()
        return np.var(qtd_alocacoes_por_pessoa)
  
    @property
    def solucao(self):
        return self._solucao
    
    @property
    def score_total(self):
        return self._score_total

    @property
    def score_vertical(self):
        return self._score_vertical

    @property
    def score_horizontal(self):
        return self._score_horizontal
    
    @property
    def tempo_execucao(self):
        return self._tempo_execucao
