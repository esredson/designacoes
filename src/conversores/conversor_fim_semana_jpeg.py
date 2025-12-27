import cv2
import easyocr
import numpy as np
import json
import os
import sys
import re
import argparse
import warnings
from difflib import get_close_matches
try:
    from conversores.conversor import Conversor
except ImportError:
    from conversor import Conversor

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pin_memory.*")

# Adiciona src ao path para importar util se necessário
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
import util

class ConversorFimSemanaJpeg(Conversor):
    def __init__(self, config):
        chaves_permitidas = ['presidente_fim_semana', 'orador', 'sentinela', 'leitura_sentinela']
        super().__init__(config, chaves_permitidas)

        # Inicializa o leitor do EasyOCR para português
        if self.debug:
            print("Inicializando EasyOCR (isso pode demorar um pouco na primeira vez)...")
        self.reader = easyocr.Reader(['pt'], gpu=False, verbose=False)

    def executar(self):
        nome_arquivo_jpeg = f'{self.ano}-{self.mes:02d}-predefinidas-fim-semana.jpeg'
        nome_arquivo_json = f'{self.ano}-{self.mes:02d}-predefinidas-fim-semana.json'
        
        caminho_jpeg = os.path.join('data', nome_arquivo_jpeg)
        caminho_json = os.path.join('data', nome_arquivo_json)
        
        if not os.path.exists(caminho_jpeg):
             print(f"Aviso: Arquivo JPEG não encontrado: {caminho_jpeg}")
             return False

        print(f"Convertendo {caminho_jpeg}...")
        self.extrair(caminho_jpeg, caminho_json)
        return True

    def extrair(self, caminho_imagem, caminho_json_saida):
        if not os.path.exists(caminho_imagem):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")

        img = cv2.imread(caminho_imagem)
        if img is None:
            raise ValueError(f"Falha ao carregar imagem: {caminho_imagem}")

        # Converter para HSV para detectar barras azuis
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # H: 80-140, S: 30-255, V: 30-255
        lower_blue = np.array([80, 30, 30])
        upper_blue = np.array([140, 255, 255])
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # DEBUG: Salvar máscara
        if self.debug:
            debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'debug')
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            debug_mask_path = os.path.join(debug_dir, 'debug_mask.png')
            cv2.imwrite(debug_mask_path, mask)
        
        # Encontrar contornos das barras
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos
        barras = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 50 and h > 5: 
                barras.append((x, y, w, h))
        
        # Ordenar de cima para baixo
        barras.sort(key=lambda b: b[1])
        
        designacoes = {}
        
        for i, (x, y, w, h) in enumerate(barras):
            self._log(f"--- Processando Seção {i} ---")
            
            # 1. Extrair Data (À direita da barra azul)
            x_data_inicio = x + w
            x_data_fim = min(img.shape[1], x_data_inicio + 400)
            
            roi_data = img[y:y+h, x_data_inicio:x_data_fim]
            
            if self.debug:
                debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'debug')
                cv2.imwrite(os.path.join(debug_dir, f'debug_crop_data_{i}.png'), roi_data)

            resultados_data = self._ocr_full(roi_data)
            
            data_str = ""
            for bbox, text, prob in resultados_data:
                match = re.search(r'\d{1,2}[\s/-]*\d{1,2}([\s/-]*\d{2,4})?', text)
                if match:
                    data_str = match.group(0).replace(" ", "")
                    self._log(f"DEBUG: Data encontrada via OCR: {data_str}")
                    break
            
            if not data_str:
                msg = f"Seção {i}: Nenhuma data encontrada à direita da barra."
                self._log(f"DEBUG: {msg}")
                self.relatorio_erros['outros_erros'].append(msg)
                continue
                
            # 2. Definir região da tabela
            y_inicio_tabela = y + h
            if i < len(barras) - 1:
                y_fim_tabela = barras[i+1][1]
            else:
                y_fim_tabela = img.shape[0]
                
            if y_fim_tabela - y_inicio_tabela > 400:
                y_fim_tabela = y_inicio_tabela + 400
                
            roi_tabela = img[y_inicio_tabela:y_fim_tabela, x:x+w]
            
            # OCR na tabela
            resultados_tabela = self._ocr_full(roi_tabela)
            
            # Agrupar por linhas (Y)
            todos_itens = []
            for bbox, text, prob in resultados_tabela:
                center_y = (bbox[0][1] + bbox[3][1]) / 2
                center_x = (bbox[0][0] + bbox[1][0]) / 2
                todos_itens.append({'text': text, 'y': center_y, 'x': center_x})
            
            todos_itens.sort(key=lambda k: k['y'])
            
            linhas_agrupadas = []
            if todos_itens:
                linha_atual = [todos_itens[0]]
                for item in todos_itens[1:]:
                    if abs(item['y'] - linha_atual[0]['y']) < 20:
                        linha_atual.append(item)
                    else:
                        linhas_agrupadas.append(linha_atual)
                        linha_atual = [item]
                linhas_agrupadas.append(linha_atual)
            
            lista_designacoes = []
            
            for linha in linhas_agrupadas:
                linha.sort(key=lambda k: k['x'])
                texto_linha = " ".join([i['text'] for i in linha])
                texto_lower = texto_linha.lower()
                
                self._log(f"DEBUG: Linha detectada: '{texto_linha}'")
                
                chave_funcao = None
                nome_pessoa_extraido = ""
                
                # Identificação da Função Dinâmica
                # Ordenar chaves por tamanho do nome (decrescente) para evitar falsos positivos em substrings
                nomes_funcoes_ordenados = sorted(self.mapa_funcoes.keys(), key=len, reverse=True)
                
                # Normalização de aspas para facilitar o match (OCR pode confundir ' com ")
                texto_lower_norm = texto_lower.replace("'", '"')
                
                for nome_role_config in nomes_funcoes_ordenados:
                    # Normaliza também a chave do config (embora já deva estar ok)
                    nome_role_config_norm = nome_role_config.replace("'", '"')
                    
                    if nome_role_config_norm in texto_lower_norm:
                        chave_funcao = self.mapa_funcoes[nome_role_config]
                        
                        # Extração do Nome
                        # Remove o nome do cargo do texto original para sobrar (provavelmente) o nome
                        # Usando regex para remover case-insensitive e possíveis dois pontos
                        # Escapa caracteres especiais do regex que possam existir no nome do cargo
                        # Precisamos ser cuidadosos com as aspas no regex
                        pattern_str = re.escape(nome_role_config_norm) + r'[:\s]*'
                        
                        # Aplica no texto normalizado para garantir que removemos o cargo corretamente
                        # Mas queremos preservar o case do nome original...
                        # Vamos tentar remover do texto original usando uma busca insensível a case e aspas
                        
                        # Estratégia simplificada: substituir no texto normalizado e depois tentar recuperar o original?
                        # Ou simplesmente usar o texto normalizado para extração do nome (já que vamos buscar no config depois)
                        
                        texto_sem_cargo = re.sub(pattern_str, '', texto_lower_norm, flags=re.IGNORECASE).strip()
                        
                        # Tenta recuperar o casing original (opcional, mas bom para debug)
                        # Como vamos buscar no config (que é case insensitive ou normalizado), usar lower aqui é aceitável.
                        # Mas para o relatório de erros, seria bom ter o nome original.
                        # Vamos usar o texto_sem_cargo (lower) por enquanto, pois o match no config é robusto.
                        
                        # Se precisarmos do nome original (Case Preserved), teríamos que fazer um match mais complexo
                        # considerando a variação de aspas no texto original.
                        # Dado o erro do OCR, talvez seja melhor confiar no lower_norm.
                        nome_pessoa_extraido = texto_sem_cargo
                        
                        if chave_funcao == 'orador':
                            # Lógica específica para Orador (Congregação/Hífen)
                            if '-' in texto_sem_cargo:
                                nome_pessoa_extraido = texto_sem_cargo.split('-')[0]
                            else:
                                nome_pessoa_extraido = texto_sem_cargo
                            
                            if "congregação" in nome_pessoa_extraido.lower():
                                nome_pessoa_extraido = re.split(r'congregação', nome_pessoa_extraido, flags=re.IGNORECASE)[0]
                        
                        # Capitaliza palavras para ficar bonito no relatório se não for encontrado
                        nome_pessoa_extraido = nome_pessoa_extraido.title()
                            
                        break # Encontrou a função, para de procurar
                
                # Validação e Mapeamento
                if chave_funcao and nome_pessoa_extraido and len(nome_pessoa_extraido) > 2:
                    nome_pessoa_extraido = nome_pessoa_extraido.strip()
                    
                    # Validar e Mapear Pessoa
                    chave_pessoa = self._encontrar_chave_por_nome(nome_pessoa_extraido, self.mapa_pessoas, 'pessoa')
                    
                    if chave_pessoa:
                        lista_designacoes.append({
                            "tipo": chave_funcao,
                            "pessoa": chave_pessoa # Usa a chave (ID) do config
                        })
                    else:
                        # Se não encontrou no config, NÃO adiciona ao JSON (conforme solicitado)
                        # Mas continua reportando no log de erros
                        pass
            
            if data_str:
                designacoes[data_str] = lista_designacoes

        # Gerar JSON
        saida = {"designacoes_predefinidas": designacoes}
        
        self.salvar_json(saida, caminho_json_saida)
        self.exibir_relatorio()
            
    def _ocr_full(self, imagem):
        try:
            return self.reader.readtext(imagem)
        except Exception as e:
            if self.debug:
                print(f"Erro no OCR: {e}")
            return []

if __name__ == "__main__":
    from inicializacao import inicializar

    try:
        # Inicialização centralizada
        args, config, mes, ano = inicializar(descricao='Converte JPEG de designações para JSON.')

        conversor = ConversorFimSemanaJpeg(config)
        conversor.executar()
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)
