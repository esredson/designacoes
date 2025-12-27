# Alocador de Tarefas

Este projeto automatiza a criação de escalas de tarefas, utilizando algoritmos de otimização para distribuir atividades de forma equilibrada entre os membros de uma equipe, respeitando restrições e impedimentos.

## Pré-requisitos

- Python 3.8 ou superior.
- As bibliotecas Python necessárias para manipulação de dados, visão computacional e leitura de arquivos (ex: `pandas`, `numpy`, `opencv-python`, `easyocr`, `pdfplumber`).

## Preparação do Ambiente

1.  Clone este repositório.
2.  Crie um ambiente virtual (recomendado):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```
3.  Instale as dependências do projeto.

## Configuração Inicial

Antes de executar a ferramenta pela primeira vez, é necessário configurar o ambiente:

1.  **Configuração Geral (`config/config.json`)**:
    - Edite o arquivo `config/config.json` para definir:
        - A lista de **pessoas** disponíveis.
        - As **funções** (tarefas) e quem está habilitado para cada uma.
        - As **colisões proibidas** (quais tarefas não podem ser realizadas simultaneamente pela mesma pessoa).
        - As regras de **tarefas predefinidas** (ex: mapeamento de nomes de atividades externas para tipos de função interna).

2.  **Arquivos de Entrada**:
    - Coloque os arquivos de entrada necessários para os conversores na pasta `data/`.
    - Estes arquivos (imagens ou PDFs contendo a programação externa) devem seguir o padrão de nomenclatura esperado pelo sistema para o mês e ano desejados.

## Execução

Para gerar as escalas para um mês específico, execute o script principal a partir da raiz do projeto:

```bash
python src/main.py --mes <MES> --ano <ANO>
```

Exemplo para Dezembro de 2025:

```bash
python src/main.py --mes 12 --ano 2025
```

### Modo Debug

Para visualizar detalhes do processo, logs detalhados dos conversores e pontuações do algoritmo passo-a-passo, utilize a flag `--debug`:

```bash
python src/main.py --mes 12 --ano 2025 --debug
```

## Como Funciona o Algoritmo

O sistema utiliza uma meta-heurística chamada **Simulated Annealing** (Recozimento Simulado) para encontrar a melhor distribuição possível das tarefas.

1.  **Solução Inicial**: O processo começa gerando uma solução válida. As pessoas são distribuídas inicialmente usando filas aleatórias para garantir que, desde o começo, a carga de trabalho seja razoavelmente equilibrada e todas as restrições rígidas sejam respeitadas.
2.  **Otimização**: O algoritmo realiza milhares de iterações. Em cada passo, ele tenta fazer uma pequena alteração na escala (trocar duas pessoas de dia ou substituir uma pessoa por outra disponível).
3.  **Critério de Aceitação**:
    - Se a nova escala for melhor (tiver uma pontuação de penalidade menor), ela é aceita imediatamente.
    - Se for pior, ela ainda pode ser aceita com uma pequena probabilidade (que diminui progressivamente), para evitar que o algoritmo fique preso em soluções que parecem boas localmente mas não são a melhor globalmente.

### Pontuação (Scores)

O algoritmo busca minimizar uma pontuação composta por três métricas principais:

1.  **Variância Vertical (Intervalo entre tarefas)**: Penaliza quando a mesma pessoa é designada em dias muito próximos (ex: dias consecutivos). O objetivo é espaçar as tarefas de uma pessoa o máximo possível.
2.  **Variância Horizontal (Equilíbrio entre funções)**: Penaliza se uma pessoa faz muito uma função e pouco outra para a qual também está habilitada. O objetivo é que a pessoa atue em todas as funções que sabe fazer de forma equilibrada.
3.  **Variância de Distribuição (Carga total)**: Penaliza o desequilíbrio na quantidade total de tarefas entre as pessoas. O objetivo é que todos trabalhem uma quantidade similar de vezes no mês.

### Restrições e Colisões

O sistema respeita rigorosamente as seguintes regras (Hard Constraints):

- **Colisões Proibidas**: Definidas no `config.json`. Por exemplo, se a "Função A" colide com a "Função B", o sistema nunca colocará a mesma pessoa nessas duas funções no mesmo dia.
- **Unicidade Diária**: Uma pessoa não pode ser designada para duas funções dinâmicas no mesmo dia, a menos que explicitamente permitido. O algoritmo verifica se a pessoa já está alocada no dia antes de tentar atribuir uma nova função.

## Execução Modular

O sistema é modular. Se você precisar rodar apenas uma etapa específica (por exemplo, apenas converter os arquivos ou apenas rodar o alocador sem converter novamente), você pode chamar os módulos diretamente através de seus pontos de entrada (`entrypoints`).

Certifique-se de estar na raiz do projeto ao executar estes comandos:

- **Apenas Conversores**:
  Os conversores podem ser executados individualmente para ler os arquivos de entrada e gerar os JSONs de tarefas predefinidas na pasta `data/`.
  ```bash
  python src/conversores/<nome_do_conversor>.py --mes 12 --ano 2025
  ```

- **Apenas Alocador**:
  Lê os JSONs de configuração e os dados já existentes na pasta `data/` para gerar a escala otimizada.
  ```bash
  python src/alocador.py --mes 12 --ano 2025
  ```

- **Apenas Gerador de PDF**:
  Gera o PDF final formatado a partir do arquivo CSV gerado pelo alocador.
  ```bash
  python src/gerador_pdf.py --mes 12 --ano 2025
  ```
