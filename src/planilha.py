
import datetime

class Planilha:
	def __init__(df, config):
		self._df = df
		self._config = config
		self._abrir_planilha()

    def _abrir_planilha(self):
        credentials = Credentials.from_service_account_file('config/credenciais_google.json')
        client = gspread.authorize(credentials)
        self._spreadsheet = client.open(config['nome_planilha'])
     
    def _get_nome_nova_aba(self):
    	mes_atual = datetime.datetime.now().strftime('%B')
        ano_atual = datetime.datetime.now().year()
        return f"{mes_atual}_{ano_atual}"
    
    def _backup_se_aba_jah_existir(self, nome_aba):
    	aba_existe = any(sheet.title == nome_aba for sheet in self _spreadsheet.worksheets())
        if not aba_existe:
        	return
        num_backup = 0
        while True:
            num_backup += 1
            nome_aba_backup = f"{nome_aba}_backup_{num_backup}"
            if not any(sheet.title == nome_aba_backup for sheet in self._spreadsheet.worksheets()):
                break
        aba_atual = self._spreadsheet.worksheet(nome_aba)
        aba_atual.update_title(nome_aba_backup)

    def _criar_aba(self, nome_aba):     
        aba_modelo = self._spreadsheet.worksheet('Modelo')
        nova_aba = self._spreadsheet.duplicate_sheet(aba_modelo.id, new_sheet_name=nome_aba)
        return self._spreadsheet.worksheet(nome_aba)
      
    def _preencher_tabela(self, aba):  
        self._preencher_funcoes(aba)
        self._preencher_datas(aba)
        self._preencher_nomes(aba)
        
    def _preencher_funcoes(self, aba):
    	indice_coluna_modelo = self._config.['coluna_modelo']
        coluna_modelo = aba.col_values(ord(indice_coluna_modelo))
        for col, funcao in df.columns:
        	indice_nova_coluna = chr(ord('C') + col)
            aba.add_cols(1) # como inserir sem ser na ult posição?
            aba.update(f'{indice_nova_coluna}:{indice_nova_coluna}', coluna_modelo)

    def _preencher_datas(self, aba):
    	for lin in df.index:
    	
    def _preencher_nomes(self, aba):

    def gerar(self):
    	nome_aba = self._get_nome_nova_aba()
    	self._backup_se_aba_jah_existir(nome_aba)
        aba = self._criar_aba(nome_aba)
   
        