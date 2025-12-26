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

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pin_memory.*")

# Adiciona src ao path para importar util se necessário
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
import util

class ConversorFimSemanaJpeg:
    def __init__(self, mes, ano, debug=False):
        self.mes = mes
        self.ano = ano
        self.debug = debug
        
        # Carregar configurações
        self.config_funcional = util.config('funcional')
        self.pessoas_config = self.config_funcional.get('pessoas', {})
        self.tipos_designacoes = self.config_funcional.get('tipos_designacoes_predefinidas', {})
        
        # Mapeamento reverso: Nome de Exibição -> Chave (ID)
        # Restringindo apenas às chaves solicitadas
        chaves_permitidas = ['presidente_fim_semana', 'orador', 'sentinela', 'leitura_sentinela']
        self.mapa_funcoes = {}
        for chave, dados in self.tipos_designacoes.items():
            if chave in chaves_permitidas:
                nome_exibicao = dados.get('nome', '').lower()
                self.mapa_funcoes[nome_exibicao] = chave
                
        # Mapeamento reverso de pessoas: Nome de Exibição -> Chave (ID)
        self.mapa_pessoas = {}
        for chave, dados in self.pessoas_config.items():
            nome_exibicao = dados.get('nome', '').lower()
            self.mapa_pessoas[nome_exibicao] = chave

        # Inicializa o leitor do EasyOCR para português
        if self.debug:
            print("Inicializando EasyOCR (isso pode demorar um pouco na primeira vez)...")
        self.reader = easyocr.Reader(['pt'], gpu=False, verbose=False)
        
        # Relatório de erros
        self.relatorio_erros = {
            'pessoas_nao_encontradas': set(),
            'funcoes_nao_encontradas': set(),
            'outros_erros': []
        }

    def _log(self, msg):
        if self.debug:
            print(msg)

    def _encontrar_chave_por_nome(self, texto, mapa, tipo_item):
        # Tenta encontrar a chave correspondente ao texto no mapa fornecido
        texto_lower = texto.lower().strip()
        
        # 1. Tentativa exata
        if texto_lower in mapa:
            return mapa[texto_lower]
            
        for nome_exibicao, chave in mapa.items():
            # 2. Config contido no Texto (Ex: Config="Pedro", Text="Pedro Silva")
            if nome_exibicao in texto_lower:
                return chave
            # 3. Texto contido no Config (Ex: Config="Pedro Silva", Text="Pedro")
            # IMPORTANTE: Apenas se for no início para evitar falsos positivos com sobrenomes (Ex: "Souza" em "Marcelo Souza")
            if nome_exibicao.startswith(texto_lower):
                return chave
        
        # 4. Tentativa fuzzy (difflib) - Cutoff alto para evitar falsos positivos (Ex: Marcelo Souza != João Souza)
        matches = get_close_matches(texto_lower, mapa.keys(), n=1, cutoff=0.8)
        if matches:
            return mapa[matches[0]]
            
        # Se não encontrar
        if tipo_item == 'pessoa':
            self.relatorio_erros['pessoas_nao_encontradas'].add(texto)
        elif tipo_item == 'funcao':
            self.relatorio_erros['funcoes_nao_encontradas'].add(texto)
            
        return None

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
        
        with open(caminho_json_saida, 'w', encoding='utf-8') as f:
            json.dump(saida, f, indent=4, ensure_ascii=False)
        
        print(f"JSON gerado em: {caminho_json_saida}")
        print(json.dumps(saida, indent=4, ensure_ascii=False))
        
        # Exibir Relatório
        if self.debug or self.relatorio_erros['pessoas_nao_encontradas'] or self.relatorio_erros['funcoes_nao_encontradas'] or self.relatorio_erros['outros_erros']:
            if self.relatorio_erros['pessoas_nao_encontradas']:
                print("\n[!] Pessoas não encontradas no config.json:")
                for p in self.relatorio_erros['pessoas_nao_encontradas']:
                    print(f"    - {p}")
            else:
                if self.debug:
                    print("\n[OK] Todas as pessoas foram encontradas no config.")
                
            if self.relatorio_erros['funcoes_nao_encontradas']:
                print("\n[!] Funções não encontradas no config.json:")
                for f in self.relatorio_erros['funcoes_nao_encontradas']:
                    print(f"    - {f}")
                    
            if self.relatorio_erros['outros_erros']:
                print("\n[!] Outros erros:")
                for e in self.relatorio_erros['outros_erros']:
                    print(f"    - {e}")
                    
            print("\n" + "="*30)
            
    def _ocr_full(self, imagem):
        try:
            return self.reader.readtext(imagem)
        except Exception as e:
            if self.debug:
                print(f"Erro no OCR: {e}")
            return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converte JPEG de designações para JSON.')
    parser.add_argument('--debug', action='store_true', help='Ativa modo debug (logs e imagens)')
    args = parser.parse_args()

    try:
        mes, ano = util.obter_mes_ano_referencia()
        nome_arquivo_jpeg = f'{ano}-{mes:02d}-predefinidas-fim-semana.jpeg'
        nome_arquivo_json = f'{ano}-{mes:02d}-predefinidas-fim-semana.json'
        
        caminho_jpeg = os.path.join('data', nome_arquivo_jpeg)
        caminho_json = os.path.join('data', nome_arquivo_json)
        
        print(f"Convertendo {caminho_jpeg}...")
        
        conversor = ConversorFimSemanaJpeg(mes, ano, debug=args.debug)
        conversor.extrair(caminho_jpeg, caminho_json)
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)
