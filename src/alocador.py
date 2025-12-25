import pandas as pd
import random
import time
import util
import numpy as np
import math

#from tqdm import tqdm

class Alocador:

    def __init__(self, funcional, agenda, designacoes_predefinidas):
        self._funcional = funcional
        self._agenda = agenda
        self._designacoes_predefinidas = designacoes_predefinidas
        self._solucao = None
        self._score_total = None
        self._score_vertical = None
        self._score_horizontal = None
        self._score_distribuicao = None
        self._tempo_execucao = None

    def executar(self, num_passos=10000, peso_vertical=1.0, peso_horizontal=1.0, peso_distribuicao=1.0, temp_inicial=100.0, resfriamento=0.995):
        inicio = time.time()
        
        # Pre-calcula contagem de designacoes predefinidas
        designacoes_predefinidas_counts = self._contar_designacoes_predefinidas_por_pessoa()

        # Solução inicial
        atual_solucao = self._alocar()
        
        # Scores iniciais
        score_v = self._quantificar_variancia_vertical(atual_solucao)
        score_h = self._quantificar_variancia_horizontal(atual_solucao)
        score_d = self._quantificar_variancia_distribuicao(atual_solucao, designacoes_predefinidas_counts)
        atual_score = (score_v * peso_vertical) + (score_h * peso_horizontal) + (score_d * peso_distribuicao)
        
        melhor_solucao = atual_solucao.copy()
        melhor_score_total = atual_score
        melhor_score_vertical = score_v
        melhor_score_horizontal = score_h
        melhor_score_distribuicao = score_d
        
        temp = temp_inicial
        
        for _ in range(num_passos):
            vizinho = self._gerar_vizinho(atual_solucao)
            
            score_v_viz = self._quantificar_variancia_vertical(vizinho)
            score_h_viz = self._quantificar_variancia_horizontal(vizinho)
            score_d_viz = self._quantificar_variancia_distribuicao(vizinho, designacoes_predefinidas_counts)
            vizinho_score = (score_v_viz * peso_vertical) + (score_h_viz * peso_horizontal) + (score_d_viz * peso_distribuicao)
            
            delta = vizinho_score - atual_score
            
            # Critério de aceitação do Simulated Annealing
            aceitar = False
            if delta < 0:
                aceitar = True
            else:
                try:
                    probabilidade = math.exp(-delta / temp)
                except OverflowError:
                    probabilidade = 0
                if random.random() < probabilidade:
                    aceitar = True
            
            if aceitar:
                atual_solucao = vizinho
                atual_score = vizinho_score
                
                # Atualiza o melhor global encontrado
                if atual_score < melhor_score_total:
                    melhor_solucao = atual_solucao.copy()
                    melhor_score_total = atual_score
                    melhor_score_vertical = score_v_viz
                    melhor_score_horizontal = score_h_viz
                    melhor_score_distribuicao = score_d_viz
            
            temp *= resfriamento
            if temp < 0.0001: # Otimização: parar se esfriar demais
                 break

        self._solucao = melhor_solucao
        self._score_total = melhor_score_total
        self._score_vertical = melhor_score_vertical
        self._score_horizontal = melhor_score_horizontal
        self._score_distribuicao = melhor_score_distribuicao
        self._tempo_execucao = time.time() - inicio

        self._solucao = self._solucao.applymap(lambda v: self._funcional.pessoas[v]['nome'])

    def _gerar_vizinho(self, solucao):
        nova_solucao = solucao.copy()
        datas = self._agenda.datas_validas
        funcoes = list(self._funcional.funcoes.keys())
        
        # Tenta encontrar uma troca válida (limite de tentativas para não travar)
        for _ in range(20):
            dt = random.choice(datas)
            funcao1 = random.choice(funcoes)
            
            pessoa1 = nova_solucao.at[dt, funcao1]
            
            # Candidato a troca: qualquer pessoa que saiba fazer a função
            candidatos = self._funcional.funcoes[funcao1]['pessoas']
            pessoa2 = random.choice(candidatos)
            
            if pessoa1 == pessoa2:
                continue
                
            # Verifica se pessoa2 já está alocada neste dia em outra função
            funcao2 = None
            for f in funcoes:
                if f != funcao1 and nova_solucao.at[dt, f] == pessoa2:
                    funcao2 = f
                    break
            
            if funcao2:
                # Caso de Troca (Swap)
                # Verifica se pessoa1 sabe fazer a funcao2
                if pessoa1 not in self._funcional.funcoes[funcao2]['pessoas']:
                    continue
                
                # Verifica impedimentos (hard constraints)
                if (self._pessoa_estah_impedida_para_a_funcao_na_data(pessoa2, funcao1, dt) or
                    self._pessoa_estah_impedida_para_a_funcao_na_data(pessoa1, funcao2, dt)):
                    continue
                
                # Realiza a troca
                nova_solucao.at[dt, funcao1] = pessoa2
                nova_solucao.at[dt, funcao2] = pessoa1
                return nova_solucao
                
            else:
                # Caso de Substituição (pessoa2 está livre no dia)
                # Verifica impedimentos
                if self._pessoa_estah_impedida_para_a_funcao_na_data(pessoa2, funcao1, dt):
                    continue
                    
                nova_solucao.at[dt, funcao1] = pessoa2
                return nova_solucao
                
        return nova_solucao

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
        for x in self._designacoes_predefinidas.datas[dt]:
            if (
                x['tipo'] in self._funcional.colisoes_proibidas.keys() 
                and funcao in self._funcional.colisoes_proibidas[x['tipo']] 
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
    
    def _contar_designacoes_predefinidas_por_pessoa(self):
        counts = {p: 0 for p in self._funcional.pessoas.keys()}
        for dt, assignments in self._designacoes_predefinidas.datas.items():
            for assignment in assignments:
                pessoa = assignment['pessoa']
                tipo = assignment['tipo']
                
                if self._funcional.tipos_designacoes_predefinidas[tipo].get('desconsiderar_ao_contar_designacoes'):
                    continue

                if pessoa in counts:
                    counts[pessoa] += 1
        return counts

    def _quantificar_variancia_distribuicao(self, df, designacoes_predefinidas_counts):
        # Count occurrences in the current solution
        solution_counts = pd.Series(df.values.flatten()).value_counts()
        
        # Combine with designacoes_predefinidas counts
        total_counts = []
        for pessoa in self._funcional.pessoas.keys():
            count = solution_counts.get(pessoa, 0) + designacoes_predefinidas_counts.get(pessoa, 0)
            total_counts.append(count)
            
        return np.var(total_counts)

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
    def score_distribuicao(self):
        return self._score_distribuicao
    
    @property
    def tempo_execucao(self):
        return self._tempo_execucao
