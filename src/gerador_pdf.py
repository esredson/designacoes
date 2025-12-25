from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import pandas as pd
import util

class GeradorPDF:
    def __init__(self, configuracoes_gerais, mes, ano):
        self._config = configuracoes_gerais
        self._mes = mes
        self._ano = ano

    def gerar(self, dataframe, caminho_arquivo):
        # Margens
        documento = SimpleDocTemplate(caminho_arquivo, pagesize=A4, 
                                rightMargin=1.5*cm, leftMargin=1.5*cm, 
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        elementos = []

        estilos = getSampleStyleSheet()
        
        # Estilos Personalizados
        # Título (Esquerda)
        estilo_titulo = ParagraphStyle('TitleCustom', parent=estilos['Heading1'], 
                                     fontName='Helvetica-Bold', fontSize=20, 
                                     alignment=TA_LEFT, textColor=colors.HexColor('#0c8091'),
                                     spaceAfter=0)
        
        # Subtítulo (Direita)
        estilo_subtitulo = ParagraphStyle('SubtitleCustom', parent=estilos['Heading2'], 
                                        fontName='Helvetica-Bold', fontSize=10, 
                                        alignment=TA_RIGHT, textColor=colors.HexColor('#666666'),
                                        spaceAfter=0)
        
        # Período (Mês/Ano) - Alinhado à esquerda, abaixo do título
        estilo_periodo = ParagraphStyle('PeriodoCustom', parent=estilos['Heading2'], 
                                       fontName='Helvetica-Bold', fontSize=14, 
                                       alignment=TA_LEFT, textColor=colors.HexColor('#666666'),
                                       spaceBefore=0, spaceAfter=0)

        # Tabela de Cabeçalho para Título/Subtítulo
        # Linha 1: Título (Esquerda), Subtítulo (Direita)
        # Linha 2: Período (Esquerda), Vazio (Direita)
        nome_mes = util.obter_nome_mes(self._mes).capitalize()
        texto_periodo = f"{nome_mes} de {self._ano}"

        dados_cabecalho = [
            [Paragraph(self._config.titulo, estilo_titulo), Paragraph(self._config.subtitulo, estilo_subtitulo)],
            [Paragraph(texto_periodo, estilo_periodo), ""]
        ]
        
        tabela_cabecalho = Table(dados_cabecalho, colWidths=[documento.width*0.6, documento.width*0.4])
        tabela_cabecalho.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,1), (-1,1), 8), # Adiciona preenchimento à segunda linha (Período)
        ]))
        elementos.append(tabela_cabecalho)
        elementos.append(Spacer(1, 0.5*cm))

        # Dados da Tabela Principal
        dados = []
        
        # Cabeçalhos das Colunas
        # Estilo: Texto branco, centralizado, negrito, tamanho 13, fundo #0c8091
        estilo_paragrafo_cabecalho = ParagraphStyle('HeaderPara', parent=estilos['Normal'], 
                                           fontName='Helvetica-Bold', fontSize=13, 
                                           textColor=colors.white, alignment=TA_CENTER,
                                           leading=13)
        
        # Garante que as colunas sejam strings
        cabecalhos = [Paragraph('', estilo_paragrafo_cabecalho)] + \
                  [Paragraph(str(col), estilo_paragrafo_cabecalho) for col in dataframe.columns]
        dados.append(cabecalhos)

        # Linhas
        # Outras células: cor da fonte #666666, tamanho 13
        estilo_celula = ParagraphStyle('Cell', parent=estilos['Normal'], 
                                    fontName='Helvetica-Bold', fontSize=13, 
                                    alignment=TA_CENTER, leading=13, textColor=colors.HexColor('#666666'))
        
        # Células de data: cor da fonte branca, tamanho 15 (dia/mês), 8 (dia da semana)
        estilo_celula_data = ParagraphStyle('DateCell', parent=estilos['Normal'], 
                                         fontName='Helvetica-Bold', fontSize=15, 
                                         alignment=TA_RIGHT, leading=13, textColor=colors.white)

        for index, linha in dataframe.iterrows():
            dt = pd.to_datetime(index)
            dia_mes = dt.strftime("%d/%m")
            dia_semana = util.obter_nome_dia_semana(dt)
            
            # Conteúdo da célula de data
            texto_data = f"{dia_mes}<br/><font size=8>{dia_semana}</font>"
            
            dados_linha = [Paragraph(texto_data, estilo_celula_data)] + \
                       [Paragraph(str(val) if pd.notna(val) else "-", estilo_celula) for val in linha]
            dados.append(dados_linha)

        # Larguras das Colunas
        # Coluna de data com largura fixa, outras distribuídas uniformemente
        largura_disponivel = documento.width
        largura_coluna_data = 3.5*cm # Aumentado levemente para fonte maior
        num_colunas_dados = len(dataframe.columns)
        largura_outras_colunas = (largura_disponivel - largura_coluna_data) / num_colunas_dados
        larguras_colunas = [largura_coluna_data] + [largura_outras_colunas] * num_colunas_dados

        tabela = Table(dados, colWidths=larguras_colunas, repeatRows=1)
        
        # Estilização da Tabela
        # Cores
        fundo_cabecalho = colors.HexColor('#0c8091')
        fundo_data = colors.HexColor('#7f7f7f')
        fundo_linha_claro = colors.HexColor('#f7f7f7')
        fundo_linha_escuro = colors.HexColor('#ebebeb')
        cor_grade = colors.white 

        estilo_tabela = TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0,0), (-1,0), fundo_cabecalho),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            
            # Célula Superior Esquerda (Vazia/Branca)
            ('BACKGROUND', (0,0), (0,0), colors.white),

            # Fundo da Coluna de Data (Todas as linhas exceto cabeçalho)
            ('BACKGROUND', (0,1), (0,-1), fundo_data),
            ('RIGHTPADDING', (0,1), (0,-1), 10), # Adiciona preenchimento para alinhamento à direita
            
            # Grade
            ('GRID', (0,0), (-1,-1), 2, colors.white),
            
            # Linhas
            ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,1), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,1), (-1,-1), 6),
            ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ])
        
        # Cores alternadas para linhas de dados (1 até o fim)
        for i in range(1, len(dados)):
            cor_fundo = fundo_linha_claro if i % 2 != 0 else fundo_linha_escuro # i começa em 1 (primeira linha de dados). 
            # Aplica apenas às colunas de dados (1 a -1)
            estilo_tabela.add('BACKGROUND', (1, i), (-1, i), cor_fundo)

        tabela.setStyle(estilo_tabela)
        elementos.append(tabela)

        documento.build(elementos)
