# Projeto de Inventário de Sistema

Este projeto consiste em um sistema de inventário para coletar e exibir informações de sistemas Linux. A aplicação é composta por dois componentes principais: um agente de inventário (`inventory-agent.py`) que coleta informações do sistema e as envia para um servidor, e um servidor web (`app.py`) que recebe esses dados, os armazena em um banco de dados e os exibe através de uma interface web.

## Estrutura de Diretórios
.
├── app.py
├── instance
│ └── system_info.db
├── inventory-agent.py
└── templates
├── details.html
└── index.html


### Descrição dos Arquivos

- **app.py**: Servidor web Flask que recebe os dados do inventário, armazena-os em um banco de dados SQLite e os exibe em uma interface web.
- **instance/system_info.db**: Banco de dados SQLite que armazena as informações do sistema.
- **inventory-agent.py**: Agente que coleta informações do sistema e as envia para o servidor.
- **templates/details.html**: Template HTML que exibe os detalhes de um sistema específico.
- **templates/index.html**: Template HTML que exibe uma lista de todos os sistemas coletados.

## Requisitos

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- psutil
- distro
- requests

## Instalação

1. Clone o repositório:
    ```sh
    git clone https://github.com/seu-usuario/inventario-py.git
    cd inventario-py
    ```

2. Crie um ambiente virtual e instale as dependências:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Inicie o servidor:
    ```sh
    python3 app.py
    ```

4. Execute o agente de inventário:
    ```sh
    python3 inventory-agent.py
    ```

## Uso

### Servidor Web

O servidor Flask (`app.py`) expõe as seguintes rotas:

- **`/`**: Página inicial que exibe uma lista de sistemas coletados.
- **`/details/<int:id>`**: Página que exibe os detalhes de um sistema específico.
- **`/api/upload`**: Endpoint que recebe dados de inventário do agente e os armazena no banco de dados.

### Agente de Inventário

O agente de inventário (`inventory-agent.py`) coleta informações do sistema e as envia para o servidor através do endpoint `/api/upload`.

As informações coletadas incluem:
- Hostname
- Distribuição Linux e versão
- Versão do kernel
- Usuário logado
- Modelo da CPU
- Memória total
- Histórico de login de usuários
- Endereços IP e MAC
- Sistemas de arquivos montados
- Informações sobre o disco

## Templates

Os templates HTML utilizam Bootstrap 5.3 para estilização. Os dados são apresentados em tabelas centralizadas.

### `index.html`

Exibe uma lista de todos os sistemas coletados com informações básicas.

### `details.html`

Exibe detalhes completos de um sistema específico, incluindo histórico de login, endereços IP e MAC, sistemas de arquivos montados e informações sobre o disco.

## Exemplo de Uso

### Coletando e Enviando Dados

Execute o agente de inventário no sistema que deseja coletar as informações:
```sh
python3 inventory-agent.py
```

### Visualizando Dados
Acesse o servidor Flask no navegador em http://localhost:5000 para visualizar a lista de sistemas coletados e seus detalhes.

### Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

### Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para obter mais informações.