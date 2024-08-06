import os
import socket
import platform
import subprocess
import sys
import datetime
import requests
import psutil

# URL do arquivo dns.hosts
DNS_HOSTS_URL = 'http://192.168.2.61/dns.hosts'

# Função para instalar uma biblioteca usando pip
def install_package(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

# Instalar ou atualizar as bibliotecas com versões específicas
def install_dependencies():
    install_package('psutil')
    install_package('requests')
    install_package('urllib3==1.26.6')  # Versão compatível com requests
    install_package('chardet==3.0.4')  # Versão compatível com requests

# Tentar importar as bibliotecas e instalar se necessário
try:
    import psutil
except ImportError:
    install_dependencies()
    import psutil

try:
    import requests
except ImportError:
    install_dependencies()
    import requests

# Função para obter os endereços IP e MAC das interfaces de rede que começam com "en"
def get_network_interfaces():
    """
    Obtém as interfaces de rede do sistema que começam com "en" junto com seus endereços IP e MAC.
    
    Retorna:
        interfaces (list): Lista de tuplas contendo (nome_da_interface, ip_da_interface, mac_da_interface).
    """
    interfaces = []
    for iface_name, iface_addrs in psutil.net_if_addrs().items():
        # Considera apenas interfaces que começam com "en"
        if not iface_name.startswith('en'):
            continue
        
        ip_addr = None
        mac_addr = None
        # Verificar cada endereço associado à interface
        for addr in iface_addrs:
            if addr.family == socket.AF_INET:  # Endereço IPv4
                ip_addr = addr.address
            elif addr.family == psutil.AF_LINK:  # Endereço MAC
                mac_addr = addr.address
        if ip_addr and mac_addr:
            interfaces.append((iface_name, ip_addr, mac_addr))
    return interfaces

# Função para renomear o hostname e atualizar /etc/hosts
def rename_and_update_hosts(new_hostname):
    """
    Renomeia o hostname do sistema e atualiza o arquivo /etc/hosts.

    Args:
        new_hostname (str): O novo hostname a ser configurado.
    """
    # Renomeia o hostname
    if platform.system() == 'Linux':
        os.system(f'hostnamectl set-hostname {new_hostname}')
        print(f"Hostname alterado para: {new_hostname}")
    else:
        raise NotImplementedError("Este script é apenas para sistemas Linux.")

    # Atualiza /etc/hosts
    with open('/etc/hosts', 'r') as file:
        lines = file.readlines()

    with open('/etc/hosts', 'w') as file:
        for line in lines:
            # Substitui a linha do hostname antigo pelo novo hostname
            if line.strip().startswith('127.0.1.1'):
                file.write(f'127.0.1.1       {new_hostname}\n')
            else:
                file.write(line)

# Função para criar um arquivo de log e registrar a data e hora atuais
def log_change():
    """
    Cria um arquivo de log e registra a data e hora atuais.
    """
    log_file_path = '/var/log/utf-change-hostname'
    if not os.path.exists(log_file_path):
        # Cria e escreve no arquivo se não existir
        with open(log_file_path, 'w') as file:
            file.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        print(f"Arquivo de log criado e registrado: {log_file_path}")

# Função para buscar e definir o hostname com base na lista
def set_hostname_from_list():
    """
    Obtém a lista de hostnames a partir de um arquivo remoto, verifica se algum IP das interfaces de rede
    corresponde a um IP na lista, e se encontrar uma correspondência, renomeia o hostname do sistema.
    """
    # Obter o arquivo dns.hosts da URL
    print("Obtendo a lista de hostnames...")
    response = requests.get(DNS_HOSTS_URL)
    response.raise_for_status()  # Garante que o request foi bem-sucedido
    lines = response.text.splitlines()
    
    # Obter as interfaces de rede
    interfaces = get_network_interfaces()

    print("IPs e MACs obtidos do sistema:")
    for iface_name, iface_ip, iface_mac in interfaces:
        print(f"Interface: {iface_name}, IP: {iface_ip}, MAC: {iface_mac}")

    found = False
    for line in lines:
        line = line.strip()
        # Ignora linhas comentadas e vazias
        if line.startswith('#') or not line:
            continue
        parts = line.split()
        ip = parts[0]
        hostnames = [hostname.split('.')[0] for hostname in parts[1:]]
        
        for hostname in hostnames:
            # Verifica se o IP corresponde a alguma interface de rede
            for iface_name, iface_ip, iface_mac in interfaces:
                if iface_ip == ip:
                    if socket.gethostname() == hostname:
                        print(f"O hostname já está configurado como: {hostname}")
                        found = True
                        break
                    rename_and_update_hosts(hostname)
                    log_change()  # Registra a mudança no arquivo de log
                    found = True
                    break
            if found:
                break
        if found:
            break

    if not found:
        print("Nenhuma correspondência encontrada.")

if __name__ == '__main__':
    # Verifica se o script está sendo executado como root
    if os.geteuid() != 0:
        print("Este script precisa ser executado como root.")
        sys.exit(1)

    # Verifica se o arquivo de log já existe
    log_file_path = '/var/log/utf-change-hostname'
    if os.path.exists(log_file_path):
        print("Script já foi executado.")
        sys.exit(1)

    # Executa a função principal
    set_hostname_from_list()
