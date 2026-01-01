# Alocador de Tarefas

Este projeto automatiza a criação de escalas de tarefas, utilizando algoritmos de otimização para distribuir atividades de forma equilibrada entre os membros de uma equipe, respeitando restrições e impedimentos.

Além de equilibrar a carga de trabalho interna, o sistema é capaz de ler designações externas (através de extratores) para evitar conflitos, garantindo que uma pessoa não seja designada para uma tarefa interna se já estiver ocupada com uma designação externa no mesmo dia.

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

- **Unicidade Diária**: Para as tarefas geradas pelo sistema, uma pessoa **nunca** será designada para mais de uma função no mesmo dia. Esta é uma regra implícita e absoluta do alocador.
- **Colisões Proibidas**: Definidas no `config.json`. Esta configuração serve para evitar conflitos entre uma designação externa (vinda de um extrator) e uma designação interna.
    - Por exemplo: Se uma pessoa já está designada externamente como "Plantão Externo", você pode configurar para que ela não receba a tarefa interna de "Suporte Local" nesse mesmo dia.
    - O sistema verifica os arquivos gerados pelos extratores e, se encontrar uma pessoa ocupada com uma tarefa externa listada nas colisões proibidas, impede que ela seja alocada na tarefa interna conflitante.

## Pré-requisitos

- **Python 3.10** ou superior.
- **Poetry**: Gerenciador de dependências e ambientes virtuais Python.

## Preparação do Ambiente

Este projeto utiliza o **Poetry** para gerenciar dependências e o ambiente virtual.

1.  Clone este repositório.
2.  Certifique-se de ter o Poetry instalado. Se não tiver, instale-o seguindo a [documentação oficial](https://python-poetry.org/docs/).
3.  Na raiz do projeto, execute o comando para instalar as dependências e criar o ambiente virtual automaticamente:
    ```bash
    poetry install
    ```
4.  Para ativar o ambiente virtual criado pelo Poetry:
    ```bash
    poetry shell
    ```
    Ou, para rodar comandos diretamente sem ativar o shell:
    ```bash
    poetry run python src/main.py ...
    ```

## Configuração Inicial

Antes de executar a ferramenta, é necessário configurar o arquivo `config/config.json`. Este arquivo define quem são as pessoas, quais tarefas existem e as regras de negócio.

### Estrutura do `config.json`

O arquivo é dividido em seções principais:
- **geral**: Títulos e subtítulos para relatórios.
- **funcional**: Define as **pessoas**, as **funções** (tarefas), os **tipos de designações externas** e as **colisões proibidas** (regras de impedimento entre externo e interno).
- **agenda**: Define os dias da semana em que as tarefas ocorrem e datas específicas de **cancelamento** (feriados ou dias sem atividade).

### Exemplo de Configuração

```json
{
    "geral": {
        "titulo": "Escala de Tarefas",
        "subtitulo": "Departamento de TI"
    },
    "funcional":{
        "pessoas": {
            "joao": { "nome": "João Silva" },
            "maria": { "nome": "Maria Santos" },
            "pedro": { "nome": "Pedro Oliveira" }
        },
        "tipos_designacoes_predefinidas": {
            "plantao_externo": "Plantão Externo (Importado)",
            "viagem_corporativa": "Viagem a Trabalho"
        },
        "funcoes": {
            "suporte_nivel_1": { "pessoas": ["joao", "maria"] },
            "suporte_nivel_2": { "pessoas": ["pedro", "maria"] },
            "monitoramento": { "pessoas": ["joao", "pedro"] }
        },
        "colisoes_proibidas": {
            "plantao_externo": ["suporte_nivel_1", "suporte_nivel_2"],
            "viagem_corporativa": ["suporte_nivel_1", "suporte_nivel_2", "monitoramento"]
        }
    },
    "agenda": {
        "dias_semana": ["seg", "qua", "sex"],
        "cancelamentos": {
            "25/12/2025": "Natal"
        }
    }
}
```

## Arquivos de Entrada e Extratores

O sistema foi desenhado para ser extensível através de **Extratores**.

Muitas vezes, a disponibilidade das pessoas depende de outras escalas externas (ex: escalas de plantão, viagens, ou outras atividades). Para evitar conflitos, o sistema pode ler esses arquivos externos.

- **Arquivos de Entrada**: Devem ser colocados na pasta `data/`. Podem ser PDFs, imagens ou planilhas, dependendo do que os extratores suportam.
- **Extratores**: São módulos de código responsáveis por ler um tipo específico de arquivo e extrair as informações relevantes (quem está ocupado em qual dia).
    - O sistema carrega dinamicamente qualquer extrator presente na pasta `src/extratores/`.
    - Se um extrator encontrar um arquivo correspondente na pasta `data/`, ele processará o arquivo e gerará um JSON intermediário com as "Designações Predefinidas".
    - O Alocador lê esses JSONs e garante que as pessoas listadas neles não recebam tarefas conflitantes na escala gerada.

## Execução

O fluxo de execução do programa ocorre em etapas:

1.  **Extração**: O sistema verifica a pasta `data/` e executa os extratores. Eles convertem arquivos brutos (PDFs, Imagens) em arquivos JSON estruturados contendo as ocupações externas.
2.  **Alocação**: O algoritmo lê o `config.json` e os JSONs gerados na etapa anterior. Ele gera uma escala otimizada para o mês solicitado.
3.  **Geração de Relatório**: O resultado final é exportado (ex: para PDF).

Para gerar as escalas para um mês específico, execute o script principal:

```bash
# Exemplo: Janeiro de 2026
poetry run python src/main.py --mes 1 --ano 2026
```

### Modo Debug

Para visualizar detalhes do processo, logs detalhados dos extratores e pontuações do algoritmo passo-a-passo, utilize a flag `--debug`:


### Execução Modular

O sistema é modular. Se você precisar rodar apenas uma etapa específica (por exemplo, apenas converter os arquivos ou apenas rodar o alocador sem converter novamente), você pode chamar os módulos diretamente através de seus pontos de entrada (`entrypoints`).

Certifique-se de estar na raiz do projeto ao executar estes comandos:

- **Apenas Extratores**:
  Os extratores podem ser executados individualmente para ler os arquivos de entrada e gerar os JSONs de tarefas predefinidas na pasta `data/`.
  ```bash
  python src/extratores/<nome_do_extrator>.py --mes 12 --ano 2025
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
