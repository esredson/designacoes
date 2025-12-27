import pdfplumber
import re
import os
import sys
import argparse
try:
    from conversores.conversor import Conversor
except ImportError:
    from conversor import Conversor
import util

class ConversorMeioSemanaPdf(Conversor):
    def __init__(self, config):
        chaves_permitidas = [
            'presidente_meio_semana', 'tesouros', 'joias', 'leitura_biblia', 
            'faca_seu_melhor', 'nossa_vida_crista', 'estudo_biblico', 
            'leitura_estudo_biblico', 'oracao_inicial', 'oracao_final'
        ]
        super().__init__(config, chaves_permitidas)

    def executar(self):
        nome_arquivo_pdf = f'{self.ano}-{self.mes:02d}-predefinidas-meio-semana.pdf'
        nome_arquivo_json = f'{self.ano}-{self.mes:02d}-predefinidas-meio-semana.json'
        
        caminho_pdf = os.path.join('data', nome_arquivo_pdf)
        caminho_json = os.path.join('data', nome_arquivo_json)
        
        if not os.path.exists(caminho_pdf):
             print(f"Aviso: Arquivo PDF não encontrado: {caminho_pdf}")
             return False

        print(f"Convertendo {caminho_pdf}...")
        self.extrair(caminho_pdf, caminho_json)
        return True

    def extrair(self, caminho_pdf, caminho_json_saida):
        if not os.path.exists(caminho_pdf):
            raise FileNotFoundError(f"PDF não encontrado: {caminho_pdf}")

        designacoes = {}
        
        print(f"Abrindo PDF: {caminho_pdf}")
        
        with pdfplumber.open(caminho_pdf) as pdf:
            for i, page in enumerate(pdf.pages):
                self._log(f"--- Processando Página {i+1} ---")
                
                # Extrair palavras com coordenadas
                words = page.extract_words(keep_blank_chars=True, x_tolerance=3, y_tolerance=3)
                
                # Agrupar palavras em linhas baseadas no 'top' com tolerância
                words.sort(key=lambda w: w['top'])
                lines = {} 
                current_top = -1
                
                for w in words:
                    if current_top == -1 or abs(w['top'] - current_top) > 5: # 5px de tolerância vertical
                        current_top = w['top']
                        lines[current_top] = []
                    lines[current_top].append(w)
                
                # Ordenar linhas verticalmente
                sorted_tops = sorted(lines.keys())
                
                current_date = None
                # Se o PDF tiver múltiplas páginas, precisamos manter o current_date entre páginas?
                # Geralmente cada página pode ter várias seções ou uma seção pode quebrar.
                # Vamos assumir que a data sempre aparece no início da seção.
                # Se uma seção quebrar página, current_date deveria persistir?
                # Por simplicidade, resetamos por página, mas idealmente persistiria.
                # O user disse "The date is ... at the beginning of the section".
                
                contexto = None 
                
                for top in sorted_tops:
                    line_words = sorted(lines[top], key=lambda w: w['x0'])
                    line_text = " ".join([w['text'] for w in line_words])
                    
                    self._log(f"DEBUG: Linha (top={top}): {line_text}")
                    
                    # Detectar Data (Início de Seção)
                    # Regex: DD de NomeDoMes (Ex: "01 de Dezembro")
                    # Usar search para ser mais flexível
                    match_data = re.search(r'(\d{1,2})\s+de\s+([A-Za-zçÇ]+)', line_text, re.IGNORECASE)
                    if match_data:
                        dia = int(match_data.group(1))
                        mes_nome = match_data.group(2).lower()
                        
                        meses = {
                            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
                            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                        }
                        
                        mes_numero = meses.get(mes_nome, self.mes)
                        
                        # Assumimos ano do conversor (mesmo que o mês mude para o próximo ano)
                        data_str = f"{dia:02d}/{mes_numero:02d}/{self.ano}"
                        current_date = data_str
                        if current_date not in designacoes:
                            designacoes[current_date] = []
                        contexto = None
                        self._log(f"DEBUG: Nova seção detectada: {current_date}")
                        # NÃO continue aqui, pois pode haver "Presidente" na mesma linha
                    
                    if not current_date:
                        continue

                    # --- Identificação de Linhas Específicas ---

                    # Presidente
                    if "Presidente" in line_text:
                        # Pode ser "Presidente:" ou "Presidente"
                        parts = re.split(r'Presidente:?', line_text)
                        if len(parts) > 1:
                            nome = parts[1].strip()
                            self._adicionar_designacao(designacoes[current_date], 'presidente_meio_semana', nome)
                        continue
                        
                    # Oração Inicial
                    # Pode ser "Oração: Nome" ou "Oração Nome" (geralmente após tema bíblico)
                    # Ignora se tiver "Cântico" (que seria oração final)
                    if "Cântico" not in line_text:
                        # Caso 1: Oração: (com dois pontos) - pode estar em qualquer lugar
                        match_com_pontos = re.search(r'Oração:\s*(.+)', line_text, re.IGNORECASE)
                        if match_com_pontos:
                            self._adicionar_designacao(designacoes[current_date], 'oracao_inicial', match_com_pontos.group(1))
                            continue
                            
                        # Caso 2: Oração (sem dois pontos) - não pode estar no início (para não conflitar com oração final isolada)
                        if not line_text.strip().lower().startswith("oração"):
                            match_sem_pontos = re.search(r'\sOração\s+(.+)', line_text, re.IGNORECASE)
                            if match_sem_pontos:
                                self._adicionar_designacao(designacoes[current_date], 'oracao_inicial', match_sem_pontos.group(1))
                                continue

                    # TESOUROS (Barra)
                    if "TESOUROS" in line_text:
                        contexto = 'tesouros'
                        continue
                        
                    # Joias
                    if "Joias" in line_text:
                        contexto = None # Sai de tesouros
                        nomes = self._extrair_colunas(line_words)
                        nomes = [n for n in nomes if n.strip()]
                        
                        if nomes and len(nomes) > 1:
                            self._adicionar_designacao(designacoes[current_date], 'joias', nomes[-1])
                        else:
                            chave = self._buscar_nome_no_final(line_text)
                            if chave:
                                self._adicionar_designacao_por_chave(designacoes[current_date], 'joias', chave)
                            else:
                                nome = line_text.replace("Joias", "").strip()
                                self._adicionar_designacao(designacoes[current_date], 'joias', nome)
                        continue
                        
                    # Leitura da Bíblia
                    if "Leitura da Bíblia" in line_text:
                        contexto = None
                        nomes = self._extrair_colunas(line_words)
                        nomes = [n for n in nomes if n.strip()]
                        
                        if nomes and len(nomes) > 1:
                            self._adicionar_designacao(designacoes[current_date], 'leitura_biblia', nomes[-1])
                        else:
                            chave = self._buscar_nome_no_final(line_text)
                            if chave:
                                self._adicionar_designacao_por_chave(designacoes[current_date], 'leitura_biblia', chave)
                            else:
                                nome = line_text.replace("Leitura da Bíblia", "").strip()
                                self._adicionar_designacao(designacoes[current_date], 'leitura_biblia', nome)
                        continue
                        
                    # FAÇA SEU MELHOR (Barra Amarela)
                    if "FAÇA SEU MELHOR" in line_text:
                        contexto = 'faca_seu_melhor'
                        continue
                        
                    # NOSSA VIDA (Barra Vermelha)
                    if "NOSSA VIDA" in line_text:
                        contexto = 'nossa_vida'
                        continue
                        
                    # Estudo bíblico
                    # Case insensitive e tolerante a acentos
                    # Regex mais permissivo para garantir match
                    if re.search(r'Estudo\s*.*b[ií]blico', line_text, re.IGNORECASE):
                        contexto = None # Sai de nossa vida
                        
                        # Identificar palavras a ignorar (Estudo, bíblico, Bíblico, etc)
                        ignore = ["Estudo", "bíblico", "Bíblico", "biblico", "de", "Congregação", "Congregacao"]
                        colunas_texto = self._extrair_colunas(line_words, ignore_terms=ignore)
                        
                        # Filtrar colunas que realmente contêm pessoas conhecidas
                        pessoas_validas = []
                        for col in colunas_texto:
                            # Verifica se esta coluna contem uma pessoa valida
                            # Usamos o metodo de busca existente
                            # Mas precisamos da chave para confirmar
                            # Vamos usar uma versao simplificada ou o proprio _encontrar_chave_por_nome
                            # Porem _encontrar_chave_por_nome loga erro se nao encontrar.
                            # Queremos apenas verificar silenciosamente.
                            
                            # Hack: Usar _encontrar_chave_por_nome mas suprimir erro?
                            # Ou melhor: iterar sobre mapa_pessoas e ver se tem match
                            
                            # Vamos usar _encontrar_chave_por_nome e limpar o erro depois? Nao, feio.
                            # Vamos assumir que se _adicionar_designacao funcionar, ok.
                            # Mas precisamos saber qual indice atribuir.
                            
                            # Vamos tentar extrair a chave sem logar erro
                            chave = self._encontrar_chave_por_nome(col, self.mapa_pessoas, 'verificacao')
                            if chave:
                                pessoas_validas.append(col)
                        
                        if len(pessoas_validas) >= 1:
                            self._adicionar_designacao(designacoes[current_date], 'estudo_biblico', pessoas_validas[0])
                        if len(pessoas_validas) >= 2:
                            self._adicionar_designacao(designacoes[current_date], 'leitura_estudo_biblico', pessoas_validas[1])
                        continue

                    # Oração Final (minúsculo "oração" à esquerda)
                    # Verifica se começa com "oração" (case insensitive) e NÃO tem ":" (para não pegar Oração: inicial)
                    # E deve ser a última linha... mas difícil saber se é a última sem lookahead.
                    # Mas se aparecer, é ela.
                    if line_text.strip().lower().startswith("oração") and "Oração:" not in line_text:
                         nome = re.sub(r'^oração\s*', '', line_text, flags=re.IGNORECASE).strip()
                         self._adicionar_designacao(designacoes[current_date], 'oracao_final', nome)
                         continue
                    
                    # Oração Final (Formato "Cântico X e oração Nome")
                    match_cantico_oracao = re.search(r'Cântico\s+\d+\s+e\s+oração\s+(.+)', line_text, re.IGNORECASE)
                    if match_cantico_oracao:
                        nome = match_cantico_oracao.group(1).strip()
                        if "Comentários" not in nome:
                            self._adicionar_designacao(designacoes[current_date], 'oracao_final', nome)
                        continue

                    # --- Processamento por Contexto ---
                    
                    if contexto == 'tesouros':
                        # Nome na coluna da direita
                        # Geralmente: "Tema do discurso ... Nome"
                        # Vamos tentar pegar a última parte ou separar por gap
                        nomes = self._extrair_colunas(line_words)
                        if nomes:
                            # Filtrar nomes vazios
                            nomes = [n for n in nomes if n.strip()]
                            
                            if not nomes:
                                continue

                            # Assume que o nome é a última coluna se houver mais de uma, ou a única
                            # Mas tesouros tem tema. "Tema... Nome". Gap grande entre tema e nome.
                            if len(nomes) > 1:
                                self._adicionar_designacao(designacoes[current_date], 'tesouros', nomes[-1])
                            else:
                                # Se só tem uma string, pode ser só o tema ou tema+nome sem gap.
                                # Difícil sem mais info. Vamos tentar usar o texto todo se não tiver gap.
                                # Ou talvez o nome esteja no config e possamos validar?
                                # Por enquanto, pega tudo.
                                # FIX: Se o nome for "Augusto" e estiver no tema, e "Diego" for o designado.
                                # Se houver gap, pegamos o último. Se não houver gap, pegamos tudo.
                                # Mas se pegarmos tudo, o _adicionar_designacao vai tentar dar match no config.
                                # Se "Augusto" estiver no config e aparecer no texto, ele pode ser pego.
                                # Vamos tentar ser mais estritos: só adicionar se tiver certeza que é nome?
                                # Ou confiar no gap.
                                
                                # Tenta encontrar TODOS os nomes possíveis na string
                                # Se encontrar mais de um, pega o que estiver mais à direita (último match no texto?)
                                # Mas _adicionar_designacao faz match fuzzy e retorna o primeiro.
                                # Vamos tentar passar a string inteira e confiar que o nome da pessoa está no final?
                                # Ou tentar quebrar a string por espaços e ver se o último token é um nome?
                                # "Tema do discurso Augusto Diego" -> "Diego"
                                
                                # Vamos tentar usar a lógica de "última palavra(s) que formam um nome válido"
                                # Mas nomes podem ser compostos.
                                
                                # Melhor abordagem: Se não houve gap detectado, mas sabemos que é Tesouros,
                                # e sabemos que o nome está à direita.
                                # Vamos tentar ver se o texto termina com um nome conhecido.
                                
                                texto_completo = nomes[0]
                                self._adicionar_designacao(designacoes[current_date], 'tesouros', texto_completo)
                        # Tesouros é só uma linha de designação (o discurso). Depois vem Joias.
                        # Então podemos limpar o contexto para não pegar lixo?
                        # Mas pode ter linhas de descrição do tema.
                        # Vamos manter contexto até mudar.
                        pass

                    elif contexto == 'faca_seu_melhor':
                        if not line_text.strip(): continue
                        # Duas colunas de pessoas
                        nomes = self._extrair_colunas(line_words)
                        # Filtrar vazios
                        nomes = [n for n in nomes if n.strip()]
                        
                        # A primeira coluna é sempre a descrição da parte.
                        # Só processamos se houver mais de uma coluna (descrição + nome(s))
                        if len(nomes) > 1:
                            for nome in nomes[1:]:
                                self._adicionar_designacao(designacoes[current_date], 'faca_seu_melhor', nome)

                    elif contexto == 'nossa_vida':
                        if not line_text.strip(): continue
                        # Uma coluna de pessoa (à direita?)
                        # Geralmente "Parte ... Nome". Gap entre parte e nome.
                        nomes = self._extrair_colunas(line_words)
                        if nomes:
                            # Filtrar nomes vazios
                            nomes = [n for n in nomes if n.strip()]
                            
                            if not nomes:
                                continue

                            # Se tiver gap, o nome é o último.
                            # Se só tiver uma coluna, assumimos que é a descrição (primeira coluna) e ignoramos.
                            if len(nomes) > 1:
                                self._adicionar_designacao(designacoes[current_date], 'nossa_vida_crista', nomes[-1])
                            else:
                                # Tenta extrair do final da linha única
                                chave = self._buscar_nome_no_final(nomes[0])
                                if chave:
                                    self._adicionar_designacao_por_chave(designacoes[current_date], 'nossa_vida_crista', chave)

        self.salvar_json({"designacoes_predefinidas": designacoes}, caminho_json_saida)
        self.exibir_relatorio()

    def _buscar_nome_no_final(self, text):
        words = text.split()
        if not words: return None
        
        # Tenta últimas 3, 2, 1 palavras
        for n in [3, 2, 1]:
            if len(words) >= n:
                candidate = " ".join(words[-n:])
                chave = self._encontrar_chave_por_nome(candidate, self.mapa_pessoas, 'verificacao')
                if chave: return chave
        return None

    def _adicionar_designacao_por_chave(self, lista_designacoes, chave_funcao, chave_pessoa):
        if not chave_pessoa: return
        lista_designacoes.append({
            "tipo": chave_funcao,
            "pessoa": chave_pessoa
        })

    def _extrair_colunas(self, line_words, ignore_terms=[]):
        # Filtra palavras ignoradas
        words = [w for w in line_words if w['text'] not in ignore_terms]
        if not words:
            return []
            
        # Detectar gaps grandes (> 20px?)
        gaps = []
        for i in range(len(words)-1):
            gap = words[i+1]['x0'] - words[i]['x1']
            if gap > 15: # Tolerância de gap
                gaps.append(i)
        
        colunas = []
        start_idx = 0
        for split_idx in gaps:
            segment = words[start_idx:split_idx+1]
            text = " ".join([w['text'] for w in segment])
            colunas.append(text)
            start_idx = split_idx + 1
        
        # Último segmento
        segment = words[start_idx:]
        text = " ".join([w['text'] for w in segment])
        colunas.append(text)
        
        # self._log(f"DEBUG: _extrair_colunas: {colunas}") # Uncomment for verbose debug
        return colunas

    def _adicionar_designacao(self, lista_designacoes, chave_funcao, nome_pessoa):
        if not nome_pessoa: return
        
        # Limpeza básica
        nome_pessoa = nome_pessoa.strip()
        if not nome_pessoa: return

        self._log(f"DEBUG: _adicionar_designacao: funcao={chave_funcao}, nome='{nome_pessoa}'")
        
        # Se for Tesouros, e tivermos um texto longo (ex: "Tema... Nome"),
        # precisamos ser mais espertos.
        if chave_funcao == 'tesouros':
             # Tokenizar o texto e procurar por nomes conhecidos
             # Removes pontuação básica
             texto_limpo = re.sub(r'[.,:;-]', ' ', nome_pessoa)
             palavras = texto_limpo.split()
             
             matches = []
             for i, palavra in enumerate(palavras):
                 if len(palavra) < 3: continue
                 
                 # Tenta encontrar chave para esta palavra usando a lógica robusta (fuzzy/partial)
                 # Passamos 'verificacao' para não logar erro se não encontrar
                 chave = self._encontrar_chave_por_nome(palavra, self.mapa_pessoas, 'verificacao')
                 if chave:
                     self._log(f"DEBUG: Tesouros match: '{palavra}' -> {chave} (idx={i})")
                     matches.append((i, chave))
                 else:
                     # Fallback: Tentar match fuzzy apenas com o primeiro nome
                     # Isso ajuda se o OCR leu "Dlego" em vez de "Diego"
                     palavra_lower = palavra.lower()
                     for nome_exibicao, chave_pessoa_map in self.mapa_pessoas.items():
                         primeiro_nome = nome_exibicao.split()[0]
                         if len(primeiro_nome) < 3: continue
                         
                         # Fuzzy match com o primeiro nome
                         from difflib import SequenceMatcher
                         ratio = SequenceMatcher(None, palavra_lower, primeiro_nome).ratio()
                         if ratio > 0.8: # 80% de similaridade
                             self._log(f"DEBUG: Tesouros fuzzy match: '{palavra}' ~ '{primeiro_nome}' -> {chave_pessoa_map} (idx={i})")
                             matches.append((i, chave_pessoa_map))
                             break
             
             if matches:
                 # Ordena pelo índice (posição da palavra no texto), pegando o último
                 matches.sort(key=lambda x: x[0], reverse=True)
                 chave_pessoa = matches[0][1]
                 self._log(f"DEBUG: Tesouros escolhido: {chave_pessoa} (de {len(matches)} matches)")
                 lista_designacoes.append({
                    "tipo": chave_funcao,
                    "pessoa": chave_pessoa
                 })
                 return
             else:
                 self._log(f"DEBUG: Tesouros: Nenhum match encontrado para '{nome_pessoa}'")

        # Validar e Mapear Pessoa (Método Padrão)
        chave_pessoa = self._encontrar_chave_por_nome(nome_pessoa, self.mapa_pessoas, 'pessoa')
        self._log(f"DEBUG: Fallback search: '{nome_pessoa}' -> {chave_pessoa}")
        
        if chave_pessoa:
            lista_designacoes.append({
                "tipo": chave_funcao,
                "pessoa": chave_pessoa
            })
        else:
            # Se não encontrou, loga erro (já feito no _encontrar_chave_por_nome)
            pass

if __name__ == "__main__":
    import argparse
    from inicializacao import inicializar

    try:
        # Inicialização centralizada
        # Nota: inicializar() carrega configs que não usamos aqui, mas garante consistência de args (mes/ano)
        args, config, mes, ano = inicializar(descricao='Converte PDF de designações de meio de semana para JSON.')

        conversor = ConversorMeioSemanaPdf(config)
        conversor.executar()
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)
