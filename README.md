![Logo Ciclus](assets/logos/ciclus_logo_laranja.png)

![Logo Ciclus](assets/images/ciclus_banner.png)
# CICLUS v2.0
*CICLUS* é um software local desenvolvido para o acompanhamento do ciclo de vida de equipamentos laboratoriais na empresa **Suporte**, proporcionando acesso rápido e fácil às informações e oferecendo total visibilidade do histórico e do status de cada equipamento. Seu principal objetivo é permitir pesquisas ágeis e precisas sobre qualquer equipamento.

O software adota o mesmo padrão de identificação e categorização utilizado na aplicação principal da empresa, [**Sond**](https://www.sond.com.br), garantindo consistência e integração com os processos já existentes.

## Novidades (v2.0)
- Código Executável
- Novo README.

## 📖 Sumário

- [Funcionalidades Principais](#funcionalidades-principais)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Armazenamento de Dados (Model)](#armazenamento-de-dados-model)
- [Controle de Dados (Controllers)](#controle-de-dados-controllers)
- [Interface Gráfica](#interface-gráfica)
- [Fluxo Geral (UI / CONTROLLERS / DATA)](#fluxo-geral-ui--controllers--data)
- [Atualizações](#atualizações)
- [Licença](#licença)
- [Contato](#contato)

## Funcionalidades Principais

*CICLUS* oferece controle completo do ciclo de vida de equipamentos laboratoriais, permitindo:

- Visualizar rapidamente todos os equipamentos com informações essenciais como status, calibração e modelo.
- Criar e editar equipamentos e registros de histórico de forma ágil e prática.
- Realizar buscas avançadas por múltiplos critérios para localizar equipamentos específicos.
- Acompanhar o histórico de cada equipamento com visão clara e organizada.
- Atualizar automaticamente informações relevantes ao adicionar novos registros, simplificando a manutenção dos dados.
- Exportar todos os dados dos equipamentos e seus itens diretamente para arquivos Excel, facilitando a análise e compartilhamento das informações.



## Tecnologias Utilizadas
- **Python**: Linguagem principal do software
- **TKinter**: Criação da interface gráfica.
- **SQLite3**: Banco de dados local para armazenamento rápido e leve.
- **Matplotlib**: Criação de gráficos para análise.

## Como transportar o projeto para seu computador local.

Você pode tanto seguir os seguintes passos utilizando GIT quanto baixar diretamente os arquivos e transportar para o local desejado.

1. Clone o repositório:
```bash
git clone https://github.com/LuanSFMarques/CICLUS
```

2. Navegue até a pasta do projeto:
```bash
cd CICLUS
```

3. instale dependências:
```bash
pip install -r requirements.txt
```

4. execute o programa:
```bash
python main.py
```
ou
```bash
py main.py
```

## Como Usar o Software Ciclus
O Ciclus é um software de gerenciamento de equipamentos, estruturado em duas abas principais:
- Tela de Equipamentos
- Tela de itens de Ciclo de Vida

O objetivo do sistema é fornecer informações sobre os equipamentos de maneira rápida e prática, priorizando velocidade de acesso e facilidade de visualização em vez de detalhamento inicial extenso.

---

### Tela de Equipamentos

Ao iniciar o programa, a Tela de Equipamentos é exibida. Nela, cada equipamento apresenta as seguintes informações:
- Nome do equipamento: Nome principal exibido na SOND.
- Tipo de equipamento
- Modelo do equipamento: Identificação simplificada (não técnico) para fácil referência.
- Sigla do setor
- Status ativo/inativo
- Status de calibração

#### Representação Visual dos Status
Os dois últimos atributos são representados graficamente por cores, para rápida interpretação:
- Status de atividade
    - Quadrado menor à esquerda do item
    - Verde: ativo
    - Vermelho: inativo
- Status de calibração:
    - Retângulo maior à direita do item
    - Verde: calibrado
    - Vermelho: não calibrado
    - Azul: especial (não necessita calibração convencional)
    - Cinza: incerto (informação de calibração não disponível)

*Nota*:
- *Equipamentos com status “incerto” não possuem informações suficientes para determinar a calibração.*
- *Equipamentos “especiais” não seguem o procedimento de calibração tradicional (ex.: casagrande, peneiras de fundo).*
- *As cores permitem que o usuário identifique rapidamente o status sem necessidade de leitura detalhada.*

#### Interações por Equipamento
Cada equipamento inclui:
- ID (identificação na SOND)
- Botão Editar: Permite alterar todas as informações, exceto o ID
- Botão Excluir: Remove o equipamento e todos os itens relacionados no ciclo de vida

A lista exibe até 20 equipamentos por página. Itens adicionais são distribuídos em páginas subsequentes, acessíveis pelos botões de navegação na parte inferior.

#### Botões de Funções Principais
- *Atualizar*: Sincroniza os dados exibidos com o banco de dados, garantindo que alterações recentes sejam refletidas na tela.
- *Resumo de Calibração*: Exibe um resumo geral dos equipamentos ativos, incluindo contagem de calibrados, não calibrados, incertos e especiais.
- *Criar Equipamento*: Abre um formulário para cadastrar um novo equipamento.

**Atenção ao cadastrar novos equipamentos:**
- **O ID deve ser único; o sistema não permite duplicações.**
- **Equipamentos devem ter periodicidade definida; caso não haja, utilize o valor padrão de 12 meses.**

#### Campo “Modelo” vs. “Modelo Técnico”
- *Modelo Técnico*: Valor completo presente na SOND, contendo informações detalhadas do equipamento.
- *Modelo (simplificado)*: Identificação direta e fácil de utilizar.
    - *Ex.: Uma peneira com modelo técnico "abert 1,18mm malha 16" pode ter o modelo simplificado "16" para referência rápida.*
- O modelo simplificado é exibido na lista de equipamentos, facilitando a visualização e identificação.


## Estrutura do Projeto

O projeto segue a arquitetura MVC (Model-View-Controller):
- Model (Data): armazenamento em SQLite3.
- View (UI): interface gráfica com Tkinter.
- Controller: funções Python que interagem entre interface e banco de dados.

Organização de pastas e arquivos:
```
Assets\
    \images
    \logos
controllers\
    \equipamento_controller.py
    \itens_controller.py
data\
    database\
        ciclus.db
        PlanilhaDeEquipamentosAtualizada_5.xlsx
    excel_output\
        equipamentos_itens.xlsx
    atualizar_calibracao.py
    atualizar_tipos.py
    excel_para_sqlite.py
    init_db.py
    sqlite_para_excel.py
    tipos.py
ui\
    telas_criacao_edicao\
        tela_criacao_ciclo.py
        tela_criacao_equip.py
        tela_edicao_ciclo.py
        tela_edicao_equip.py
    telas_misc\
        tela_plano_calibr.py
    telas_principais\
        tela_desc_item.py
        tela_equipamentos.py
        tela_itens.py
helpers.py
main.py
```

## Armazenamento de Dados
A base de dados em SQLite é simples e otimizada para manter o histórico de cada equipamento.
- A tabela equipamentos é a principal e conecta-se a outras por foreign keys.
- Cada equipamento possui um conjunto ilimitado de itens no ciclo de vida.
- A leveza do SQLite garante fácil manutenção e boa performance.

<img src="assets/images/ciclus_diagrama.png" width="80%">

## Controle de Dados
Os controllers centralizam as funções de manipulação e consulta:
- equipamento_controller.py → busca, criação, edição e exclusão de equipamentos.
- itens_controller.py → gerenciamento do histórico de itens dos equipamentos.

Todas as funções incluem tratamento de erros com try/except, garantindo robustez e clareza nas operações.

## Interface Gráfica

A interface foi projetada para ser clara e funcional, com uma estética retrô e uso de cores para facilitar a navegação.

### Tela de Equipamentos

- Status do equipamento:
    - Verde → Ativo
    - Vermelho → Inativo
- Condição de calibração:
    - Verde → Calibrado
    - Vermelho → Não calibrado
    - Cinza → Incerto
    - Azul → Especial

<img src="assets/images/ciclus_tela_equipamentos.png" width="80%">

### Criação de Equipamentos
Formulário para registro de novos equipamentos, com campos obrigatórios e opcionais.

<img src="assets/images/ciclus_tela_criacao_equip.png" width="55%">

### Itens do Ciclo de Vida
Lista cronológica dos eventos relacionados a cada equipamento.

<img src="assets/images/ciclus_tela_itens.png" width="80%">

### Criação de Itens
- Data automática inserida caso o campo fique vazio.
- Atualização automática de status ou setor ao criar itens específicos.

<img src="assets/images/ciclus_tela_criacao_item.png" width="55%">

### Descrição de Itens
Detalhes adicionais sobre cada ocorrência no histórico.

<img src="assets/images/ciclus_tela_descricao.png" width="65%">

## Fluxo Geral

O fluxo segue o padrão MVC:
- O usuário interage pela interface (UI).
- O Controller processa a ação e comunica com o banco de dados.
- O Model armazena e retorna os dados atualizados.

Exemplo: ao criar um equipamento, o equipamento_controller.py recebe os dados, conecta-se ao banco e executa a query correspondente.

## Atualizações
Atualizações pendentes para as próximas versões do software podem ser encontradas a baixo:

[ROADMAP](roadmap.md)

## Licença
...

## Contato
Luan de Souza Ferreira Marques

luansfmarques@gmail.com

https://www.linkedin.com/in/luansfmarques/