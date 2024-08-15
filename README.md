# Projeto de Automação e Inventário de computadores com SO Linux

Este projeto consiste em um sistema de automação para renomeação de hostname e inventário de hardware, utilizando Python e ferramentas de configuração como Ansible.

## Estrutura do Projeto

```plaintext
.
├── app.py
├── instance
│   └── system_info.db
├── LICENSE
├── migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       └── ae9a9494ea98_make_patrimony_column_nullable.py
├── __pycache__
│   └── app.cpython-310.pyc
├── README.md
├── requirements-agent.txt
├── requirements.txt
├── setup-change-hostname.yml
├── setup-inventory-agent.yml
├── templates
│   ├── details.html
│   └── index.html
├── utf-change-hostname-from-dns.py
└── utf-inventory-agent.py
```

### Descrição dos Componentes

- **app.py**: Arquivo principal que inicia o aplicativo.
- **instance/system_info.db**: Banco de dados SQLite que armazena as informações coletadas pelo sistema.
- **LICENSE**: Arquivo de licença do projeto.
- **migrations/**: Diretório contendo scripts para gerenciar migrações de banco de dados usando Alembic.
- **__pycache__/**: Diretório que armazena arquivos Python compilados.
- **requirements-agent.txt** e **requirements.txt**: Arquivos contendo as dependências do projeto.
- **setup-change-hostname.yml** e **setup-inventory-agent.yml**: Playbooks Ansible para configurar scripts no sistema.
- **templates/**: Diretório com templates HTML para a interface web.
- **utf-change-hostname-from-dns.py** e **utf-inventory-agent.py**: Scripts Python para gerenciamento de inventário e renomeação automática de hostname.

## Scripts e Funcionalidades

### `utf-inventory-agent.py`

Este script coleta diversas informações de sistema, incluindo:

- Distribuição e versão do Linux
- Versão do kernel
- Usuário logado
- Histórico de logins de usuários
- Endereços IP e MAC das interfaces de rede
- Informações de CPU, memória, disco, sistemas de arquivos montados e GPUs
- Modelo da placa-mãe

As informações são salvas em um arquivo JSON e enviadas para um servidor de monitoramento.

### `utf-change-hostname-from-dns.py`

Este script renomeia automaticamente o hostname do sistema com base no endereço IP da máquina, consultando um arquivo de configuração remoto (`dns.hosts`). Ele também atualiza o arquivo `/etc/hosts` e registra as mudanças em um arquivo de log.

### Playbooks Ansible

#### `setup-change-hostname.yml`

Este playbook configura o serviço de renomeação automática do hostname no sistema:

- Copia o script `utf-change-hostname-from-dns.py` para `/usr/local/bin/`
- Cria e habilita um serviço `systemd` para executar o script no boot do sistema

#### `setup-inventory-agent.yml`

Este playbook configura a execução automática do script de inventário no login de cada usuário:

- Copia o script `utf-inventory-agent.py` para `/usr/local/bin/`
- Cria um script em `/etc/profile.d/` que executa o script de inventário automaticamente no login

## Requisitos

Instale as dependências listadas nos arquivos `requirements-agent.txt` e `requirements.txt` utilizando pip:

```bash
pip install -r requirements.txt
pip install -r requirements-agent.txt
```

## Uso

### Executar os Playbooks Ansible

1. **Configurar o Agente de Inventário:**

   ```bash
   ansible-playbook setup-inventory-agent.yml
   ```

2. **Configurar o Serviço de Renomeação de Hostname:**

   ```bash
   ansible-playbook setup-change-hostname.yml
   ```

### Executar Scripts Manualmente

Para coletar informações do sistema e enviá-las ao servidor, execute:

```bash
python3 utf-inventory-agent.py
```

Para renomear o hostname com base no IP, execute:

```bash
python3 utf-change-hostname-from-dns.py
```

## Licença

Este projeto está licenciado sob os termos do arquivo LICENSE.



