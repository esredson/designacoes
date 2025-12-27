import unittest
import pandas as pd
import numpy as np
import sys
import os
import datetime
from unittest.mock import MagicMock

# Adiciona src ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from alocador import Alocador

class TestAlocador(unittest.TestCase):

    def setUp(self):
        # Dependências simuladas (Mock)
        self.mock_config = MagicMock()
        self.mock_config.debug = False
        self.mock_config.diretorio_dados = 'data'
        self.mock_config.ano = 2025
        self.mock_config.mes = 12
        self.mock_config.datas_validas = []

        # Configuração básica do mock funcional
        self.mock_config.pessoas = {
            'pessoa1': {'nome': 'Pessoa 1'},
            'pessoa2': {'nome': 'Pessoa 2'}
        }
        self.mock_config.funcoes = {
            'funcao1': {'nome': 'Funcao 1', 'pessoas': ['pessoa1', 'pessoa2']},
            'funcao2': {'nome': 'Funcao 2', 'pessoas': ['pessoa1', 'pessoa2']}
        }
        
        # Inicializa o Alocador com mocks, evitando carregar arquivos reais
        with unittest.mock.patch.object(Alocador, '_carregar_designacoes_predefinidas') as mock_carregar:
            self.alocador = Alocador(self.mock_config)
            self.alocador._designacoes_predefinidas = {}

    def test_quantificar_variancia_vertical(self):
        # Cenário: 
        # pessoa1 nas linhas 0 e 1 (consecutivas) -> intervalo 1 -> score 1.0
        # pessoa2 nas linhas 0 e 2 (lacuna de 1) -> intervalo 2 -> score 0.5
        
        data = {
            'funcao1': ['pessoa1', 'pessoa1', 'pessoa2'],
            'funcao2': ['pessoa2', 'other', 'other']
        }
        df = pd.DataFrame(data)
        
        # Cálculo esperado:
        # pessoa1: linhas [0, 1]. diff=[1]. sum(1/1) = 1.0
        # pessoa2: linhas [0, 2]. diff=[2]. sum(1/2) = 0.5
        # Média = (1.0 + 0.5) / 2 = 0.75
        
        score = self.alocador._quantificar_variancia_vertical(df)
        self.assertAlmostEqual(score, 0.75)

    def test_quantificar_variancia_vertical_sparse(self):
        # Cenário: Designações esparsas
        # pessoa1 nas linhas 0 e 4 -> intervalo 4 -> score 0.25
        # pessoa2 apenas uma vez -> score 0
        
        data = {
            'funcao1': ['pessoa1', 'other', 'other', 'other', 'pessoa1'],
            'funcao2': ['other', 'other', 'pessoa2', 'other', 'other']
        }
        df = pd.DataFrame(data)
        
        # Esperado:
        # pessoa1: linhas [0, 4]. diff=[4]. score = 0.25
        # pessoa2: linhas [2]. len < 2. score = 0
        # Média = (0.25 + 0) / 2 = 0.125
        
        score = self.alocador._quantificar_variancia_vertical(df)
        self.assertAlmostEqual(score, 0.125)

    def test_quantificar_variancia_horizontal(self):
        # Cenário:
        # pessoa1: funcao1=2, funcao2=2. Equilibrado. Var([2,2]) = 0
        # pessoa2: funcao1=4, funcao2=0. Desequilibrado. Var([4,0]) = 4.0
        
        data = {
            'funcao1': ['pessoa1', 'pessoa1', 'pessoa2', 'pessoa2', 'pessoa2', 'pessoa2'],
            'funcao2': ['pessoa1', 'pessoa1', 'other', 'other', 'other', 'other']
        }
        df = pd.DataFrame(data)
        
        # Esperado:
        # pessoa1: contagens [2, 2]. var = 0
        # pessoa2: contagens [4, 0]. var = 4
        # Média = 2.0
        
        score = self.alocador._quantificar_variancia_horizontal(df)
        self.assertAlmostEqual(score, 2.0)

    def test_quantificar_variancia_distribuicao(self):
        # Cenário:
        # pessoa1: 2 no df + 1 predefinida = 3 total
        # pessoa2: 1 no df + 3 predefinidas = 4 total
        
        data = {
            'funcao1': ['pessoa1', 'pessoa1', 'pessoa2'],
            'funcao2': ['other', 'other', 'other']
        }
        df = pd.DataFrame(data)
        
        predefined_counts = {
            'pessoa1': 1,
            'pessoa2': 3
        }
        
        # Esperado:
        # pessoa1 total: 2 + 1 = 3
        # pessoa2 total: 1 + 3 = 4
        # Var([3, 4]) = 0.25
        
        score = self.alocador._quantificar_variancia_distribuicao(df, predefined_counts)
        self.assertAlmostEqual(score, 0.25)

    def test_quantificar_variancia_distribuicao_perfect(self):
        # Cenário: Distribuição perfeita
        # pessoa1: 2 no df + 2 predefinidas = 4
        # pessoa2: 4 no df + 0 predefinidas = 4
        
        data = {
            'funcao1': ['pessoa1', 'pessoa1', 'pessoa2', 'pessoa2'],
            'funcao2': ['pessoa2', 'pessoa2', 'other', 'other']
        }
        df = pd.DataFrame(data)
        
        predefined_counts = {
            'pessoa1': 2,
            'pessoa2': 0
        }
        
        # Esperado:
        # pessoa1 total: 2 + 2 = 4
        # pessoa2 total: 4 + 0 = 4
        # Var([4, 4]) = 0
        
        score = self.alocador._quantificar_variancia_distribuicao(df, predefined_counts)
        self.assertAlmostEqual(score, 0.0)

    def test_colisao_proibida_respeitada(self):
        # Configuração do cenário
        dt = datetime.date(2025, 12, 1)
        pessoa = 'pessoa_teste'
        funcao_proibida = 'funcao_proibida'
        funcao_permitida = 'funcao_permitida'
        tipo_predefinido = 'tipo_predefinido_conflitante'

        # 1. Configurar colisoes_proibidas
        # Se a pessoa tiver 'tipo_predefinido_conflitante', ela não pode fazer 'funcao_proibida'
        self.mock_config.colisoes_proibidas = {
            tipo_predefinido: [funcao_proibida]
        }

        # 2. Configurar designacoes_predefinidas
        # A pessoa tem esse tipo predefinido na data
        self.alocador._designacoes_predefinidas = {
            dt: [{'tipo': tipo_predefinido, 'pessoa': pessoa}]
        }

        # Teste 1: Verificar se a função proibida é detectada como impedida
        impedida = self.alocador._pessoa_estah_impedida_para_a_funcao_na_data(
            pessoa, funcao_proibida, dt
        )
        self.assertTrue(impedida, "A pessoa deveria estar impedida para a função proibida")

        # Teste 2: Verificar se uma função não listada nas colisões é permitida
        impedida_permitida = self.alocador._pessoa_estah_impedida_para_a_funcao_na_data(
            pessoa, funcao_permitida, dt
        )
        self.assertFalse(impedida_permitida, "A pessoa NÃO deveria estar impedida para a função permitida")

    def test_sem_designacao_predefinida(self):
        # Cenário onde não há designação predefinida na data
        dt = datetime.date(2025, 12, 2)
        pessoa = 'pessoa_teste'
        funcao = 'qualquer_funcao'
        
        self.alocador._designacoes_predefinidas = {} # Vazio
        self.mock_config.colisoes_proibidas = {'algum_tipo': ['qualquer_funcao']}

        impedida = self.alocador._pessoa_estah_impedida_para_a_funcao_na_data(
            pessoa, funcao, dt
        )
        self.assertFalse(impedida, "Sem designação predefinida, não deve haver impedimento")

    def test_designacao_predefinida_sem_conflito_configurado(self):
        # Cenário onde há designação predefinida, mas o tipo não está em colisoes_proibidas
        dt = datetime.date(2025, 12, 3)
        pessoa = 'pessoa_teste'
        funcao = 'funcao_x'
        tipo_predefinido = 'tipo_seguro'

        self.mock_config.colisoes_proibidas = {
            'outro_tipo': ['funcao_x']
        }
        self.alocador._designacoes_predefinidas = {
            dt: [{'tipo': tipo_predefinido, 'pessoa': pessoa}]
        }

        impedida = self.alocador._pessoa_estah_impedida_para_a_funcao_na_data(
            pessoa, funcao, dt
        )
        self.assertFalse(impedida, "Tipo predefinido não listado em colisões não deve gerar impedimento")

    def test_alocacao_multipla_no_mesmo_dia(self):
        # Cenário 1: Pessoa já alocada dinamicamente no mesmo dia -> Deve ser impedida
        dt = datetime.date(2025, 12, 1)
        pessoa = 'pessoa1'
        
        # Simula que pessoa1 já foi escolhida para 'funcao1' neste dia
        df = pd.DataFrame(index=[dt], columns=['funcao1', 'funcao2'])
        df.at[dt, 'funcao1'] = pessoa
        
        # Tenta verificar disponibilidade para 'funcao2'
        # _obter_proxima_pessoa_da_fila deve pular pessoa1
        fila = ['pessoa1', 'pessoa2']
        escolhido = self.alocador._obter_proxima_pessoa_da_fila(fila, 'funcao2', dt, df)
        
        self.assertNotEqual(escolhido, pessoa, "Pessoa já alocada no dia não deve ser escolhida novamente")
        self.assertEqual(escolhido, 'pessoa2')

    def test_alocacao_com_predefinicao_nao_colidente(self):
        # Cenário 2: Pessoa tem designação predefinida NÃO colidente -> Deve ser permitida
        dt = datetime.date(2025, 12, 2)
        pessoa = 'pessoa1'
        
        # Configura predefinição
        self.alocador._designacoes_predefinidas = {
            dt: [{'tipo': 'leitura', 'pessoa': pessoa}]
        }
        # Configura colisoes (leitura não colide com funcao1)
        self.mock_config.colisoes_proibidas = {
            'outra_coisa': ['funcao1']
        }
        
        df = pd.DataFrame(index=[dt], columns=['funcao1'])
        
        # Tenta alocar para funcao1
        fila = ['pessoa1']
        escolhido = self.alocador._obter_proxima_pessoa_da_fila(fila, 'funcao1', dt, df)
        
        self.assertEqual(escolhido, pessoa, "Pessoa com predefinição não colidente deve ser permitida")

    def test_simulated_annealing_execution(self):
        # Configura um cenário simples para teste de integração do algoritmo
        datas = [datetime.date(2025, 1, 1), datetime.date(2025, 1, 2)]
        self.mock_config.datas_validas = datas
        self.mock_config.funcoes = {
            'funcao1': {'pessoas': ['p1', 'p2'], 'icone': 'A', 'nome': 'Função 1'},
            'funcao2': {'pessoas': ['p2', 'p3'], 'icone': 'B', 'nome': 'Função 2'}
        }
        self.mock_config.pessoas = {
            'p1': {'nome': 'Ana Silva'},
            'p2': {'nome': 'Beto Souza'},
            'p3': {'nome': 'Carlos Lima'}
        }
        self.alocador._designacoes_predefinidas = {}
        self.mock_config.colisoes_proibidas = {}
        self.mock_config.tipos_designacoes_predefinidas = {}
        self.mock_config.cancelamentos = {}

        # Executa o algoritmo com poucos passos
        self.alocador._executar(num_passos=50, temp_inicial=10.0)

        # Verificações
        self.assertIsNotNone(self.alocador.solucao, "A solução não deve ser None")
        self.assertIsInstance(self.alocador.solucao, pd.DataFrame, "A solução deve ser um DataFrame")
        
        # Verifica dimensões (2 dias x 2 funções)
        self.assertEqual(self.alocador.solucao.shape, (2, 2))
        
        # Verifica se os scores foram calculados
        self.assertIsNotNone(self.alocador.score_total)
        
        # Verifica se os nomes foram substituídos corretamente (IDs -> Primeiros Nomes)
        valores_flat = self.alocador.solucao.values.flatten()
        nomes_esperados = ['Ana', 'Beto', 'Carlos']
        for val in valores_flat:
            self.assertIn(val, nomes_esperados, f"Valor '{val}' não é um nome esperado")

        # Verifica se as colunas viraram MultiIndex
        self.assertIsInstance(self.alocador.solucao.columns, pd.MultiIndex)

if __name__ == '__main__':
    unittest.main()
