from constraint import Problem, AllDifferentConstraint, MinConflictsSolver
import pandas as pd
import util

class CSP:

    def __init__(self, funcional, agenda, extra):
        self._funcional = funcional
        self._agenda = agenda
        self._extra = extra
        self._qtd_max_repeticoes_por_funcao = 6.0
        self._solucao = None
        
    def _criar_variaveis(self, problem):
        for i, funcao in enumerate(self._funcional.funcoes.keys()):
            for j in range(len(self._agenda.datas_validas)):
                problem.addVariable(f"{i}-{j}", self._funcional.funcoes[funcao]['pessoas'])

    def _evitar_repetir_pessoa_mesmo_dia(self, problem):
        for j in range(len(self._agenda.datas_validas)):
            problem.addConstraint(AllDifferentConstraint(),tuple(f"{i}-{j}" for i in range(len(self._funcional.funcoes))))

    def _evitar_repetir_pessoas_por_funcao(self, problem):
        for i, funcao in enumerate(self._funcional.funcoes.keys()):
            pessoas_da_funcao=self._funcional.funcoes[funcao]['pessoas']
            problem.addConstraint(
                lambda *tupla, pessoas=pessoas_da_funcao: util.calcular_qtd_repeticoes_desnecessarias(tupla, pessoas) <= self._qtd_max_repeticoes_por_funcao,
                tuple(f"{i}-{j}" for j in range(len(self._agenda.datas_validas)))
            )
            
    def _evitar_colidir_com_partes_extras(self, problem):
        for i, funcao in enumerate(self._funcional.funcoes.keys()):
            for j, data in enumerate(self._agenda.datas_validas):
                for p in self._funcional.funcoes[funcao]['pessoas']:
                    for x in self._extra.datas[data]:
                        if x['parte'] in self._funcional.colisoes_proibidas.keys() and funcao in self._funcional.colisoes_proibidas[x['parte']] and x['pessoa'] == p:
                            problem.addConstraint(lambda val, p_local=p: val != p_local, [f"{i}-{j}"])
  
    def _gerar_problema(self):
        problem = Problem(solver=MinConflictsSolver())      
        self._criar_variaveis(problem)
        self._evitar_repetir_pessoa_mesmo_dia(problem)
        self._evitar_repetir_pessoas_por_funcao(problem)
        self._evitar_colidir_com_partes_extras(problem)
        return problem
           
    def executar(self):
        problem = self._gerar_problema()
        self._solucao = problem.getSolution()

    @property
    def qtd_max_repeticoes_por_funcao(self):
        return self._qtd_max_repeticoes_por_funcao

    @qtd_max_repeticoes_por_funcao.setter
    def qtd_max_repeticoes_por_funcao(self, q):
        self._qtd_max_repeticoes_por_funcao = q

    @property
    def solucao(self):
        return self._solucao

    @property
    def solucao_formatada(self):
        if self._solucao is None:
            return None
        df = pd.DataFrame(
            columns=[self._funcional.funcoes[f]['nome'] for f in self._funcional.funcoes.keys()], 
            index=self._agenda.datas_validas
        )
        sol = self._solucao
        for i, funcao in enumerate(df.columns):
            for j, data in enumerate(df.index):
                df.at[data, funcao] = self._funcional.pessoas[sol[f'{i}-{j}']]['nome']
        
        datas_incluindo_canceladas = self._agenda.datas
        df = df.reindex(datas_incluindo_canceladas)
        df = df.sort_index()
        for dt in self._agenda.cancelamentos.keys():
            df.at[dt, df.columns[0]] = self._agenda.cancelamentos[dt]
        
        return df

    @property
    def tempo_execucao(self):
        return self._tempo_exec
