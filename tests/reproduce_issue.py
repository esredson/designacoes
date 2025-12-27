import unittest
import datetime
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from alocador import Alocador

from config import Config

class TestReproduction(unittest.TestCase):
    def test_real_config_loading(self):
        # Load real config for Dec 2025
        config = Config(12, 2025, debug=True)
        
        dt = datetime.date(2025, 12, 21)
        
        # Check if designacoes_predefinidas has entries for Dec 21st
        predefinidas = config.designacoes_predefinidas.get(dt, [])
        print(f"Predefinidas for {dt}: {predefinidas}")
        
        # Check if Edson is sentinela
        is_sentinela = any(x['tipo'] == 'sentinela' and x['pessoa'] == 'edson' for x in predefinidas)
        self.assertTrue(is_sentinela, "Edson should be loaded as sentinela from JSON")
        
        # Check collision config
        collisions = config.colisoes_proibidas.get('sentinela', [])
        print(f"Collisions for sentinela: {collisions}")
        self.assertIn('volante1', collisions)
        
        # Check Alocador logic with real config
        alocador = Alocador(config)
        is_impeded = alocador._pessoa_estah_impedida_para_a_funcao_na_data('edson', 'volante1', dt)
        print(f"Is Edson impeded? {is_impeded}")
        self.assertTrue(is_impeded)

if __name__ == '__main__':
    unittest.main()
