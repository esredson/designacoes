import unittest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Adiciona src ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.alocador import Alocador

class TestAlocador(unittest.TestCase):

    def setUp(self):
        # Dependências simuladas (Mock)
        self.mock_funcional = MagicMock()
        self.mock_agenda = MagicMock()
        self.mock_designacoes_predefinidas = MagicMock()

        # Configuração básica do mock funcional
        self.mock_funcional.pessoas = {
            'pessoa1': {'nome': 'Pessoa 1'},
            'pessoa2': {'nome': 'Pessoa 2'}
        }
        self.mock_funcional.funcoes = {
            'funcao1': {'nome': 'Funcao 1', 'pessoas': ['pessoa1', 'pessoa2']},
            'funcao2': {'nome': 'Funcao 2', 'pessoas': ['pessoa1', 'pessoa2']}
        }
        
        # Inicializa o Alocador com mocks
        self.alocador = Alocador(
            self.mock_funcional, 
            self.mock_agenda, 
            self.mock_designacoes_predefinidas
        )

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

if __name__ == '__main__':
    unittest.main()
