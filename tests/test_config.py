import unittest
import json
import sys
import os
from unittest.mock import mock_open, patch

# Adiciona src ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from config import Config

def _config_json(pesos_score=None):
    funcional = {
        "pessoas": {"p1": {"nome": "Pessoa 1"}},
        "funcoes": {"f1": {"pessoas": ["p1"]}},
        "tipos_designacoes_predefinidas": {},
        "colisoes_proibidas": {}
    }
    if pesos_score is not None:
        funcional["pesos_score"] = pesos_score

    return json.dumps({
        "geral": {"titulo": "T", "subtitulo": "S"},
        "funcional": funcional,
        "agenda": {"dias_semana": ["qua"], "cancelamentos": {}}
    })

class TestConfig(unittest.TestCase):

    def test_pesos_score_padrao_quando_ausente(self):
        # Sem a chave 'pesos_score' no config.json, os pesos devem ser 1.0 (comportamento original)
        with patch('builtins.open', mock_open(read_data=_config_json())):
            config = Config(1, 2025)

        self.assertEqual(config.peso_score_vertical, 1.0)
        self.assertEqual(config.peso_score_horizontal, 1.0)
        self.assertEqual(config.peso_score_distribuicao, 1.0)

    def test_pesos_score_customizado(self):
        pesos = {"vertical": 2.0, "horizontal": 0.5, "distribuicao": 3.0}
        with patch('builtins.open', mock_open(read_data=_config_json(pesos))):
            config = Config(1, 2025)

        self.assertEqual(config.peso_score_vertical, 2.0)
        self.assertEqual(config.peso_score_horizontal, 0.5)
        self.assertEqual(config.peso_score_distribuicao, 3.0)

if __name__ == "__main__":
    unittest.main()
