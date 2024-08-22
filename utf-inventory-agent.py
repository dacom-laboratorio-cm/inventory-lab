#!/usr/bin/env python3

import os
import pwd
import platform
import psutil
import socket
import json
import uuid
import requests
import distro
import GPUtil
from datetime import datetime
import subprocess
import sys

import logging

# Configuração do logging
log_directory = os.path.expanduser('~')
log_file = os.path.join(log_directory, '.utf-inventory-agent.log')

# Cria o diretório de logs se não existir
os.makedirs(log_directory, exist_ok=True)

# Configura o logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Função para instalar as bibliotecas necessárias
def install_packages():
    """
    Instala as bibliotecas necessárias usando pip se não estiverem instaladas.
    """
    required_packages = [
        'requests',  # Biblioteca para fazer requisições HTTP
        'distro',    # Biblioteca para obter informações sobre a distribuição Linux
        'GPUtil',    # Biblioteca para obter informações sobre GPUs NVIDIA
        'psutil'     # Biblioteca para obter informações sobre o sistema e processos
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def get_linux_distribution():
    """
    Obtém o nome e a versão da distribuição Linux.
    
    Returns:
        str: Nome e versão da distribuição Linux.
    """
    name = distro.name()
    version = distro.version()
    return f"{name} {version}"

def get_kernel_version():
    """
    Obtém a versão do kernel Linux.
    
    Returns:
        str: Versão do kernel.
    """
    return platform.release()

def get_logged_in_user():
    """
    Obtém o nome do usuário que está logado no sistema.
    
    Returns:
        str: Nome do usuário logado.
    """
    try:
        return os.getlogin()
    except OSError:
        return pwd.getpwuid(os.getuid())[0]


def get_user_login_history():
    """
    Obtém o histórico de logins de usuários no sistema.
    
    Returns:
        list: Lista de dicionários contendo informações sobre logins de usuários.
    """
    login_history = []
    with os.popen('last -F') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 7:
                login_history.append({
                    'user': parts[0],
                    'tty': parts[1],
                    'ip': parts[2],
                    'datetime': f"{parts[3]} {parts[4]} {parts[5]} {parts[6]}"
                })
    latest_logins = {}
    for entry in login_history:
        latest_logins[entry['user']] = entry
    return list(latest_logins.values())

def get_ip_and_mac_addresses():
    """
    Obtém os endereços IP e MAC das interfaces de rede.
    
    Returns:
        list: Lista de dicionários contendo informações sobre IP e MAC das interfaces.
    """
    ip_and_mac = []
    for interface, addrs in psutil.net_if_addrs().items():
        ip = None
        mac = None
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address
            elif addr.family == psutil.AF_LINK:
                mac = addr.address
        if ip and mac:
            ip_and_mac.append({'interface': interface, 'ip': ip, 'mac': mac})
    return ip_and_mac

def get_cpu_info():
    """
    Obtém informações sobre o CPU.
    
    Returns:
        dict: Dicionário contendo o modelo do CPU.
    """
    cpu_info = {}
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if 'model name' in line:
                    cpu_info['model_name'] = line.split(':')[1].strip()
                    break
    except FileNotFoundError:
        cpu_info['model_name'] = 'Unknown'
    return cpu_info

def get_memory_info():
    """
    Obtém informações sobre a memória RAM total do sistema.
    
    Returns:
        float: Memória total em GB.
    """
    mem_info = psutil.virtual_memory()
    return round(mem_info.total / (1024**3), 2)

def get_disk_info():
    """
    Obtém informações sobre o disco principal do sistema.
    
    Returns:
        dict: Dicionário contendo a capacidade total e o espaço livre do disco em GB.
    """
    disk_info = psutil.disk_usage('/')
    return {
        'total': round(disk_info.total / (1024**3), 2),
        'free': round(disk_info.free / (1024**3), 2)
    }

def get_mounted_filesystems():
    """
    Obtém informações sobre os sistemas de arquivos montados.
    
    Returns:
        list: Lista de dicionários contendo informações sobre os sistemas de arquivos montados.
    """
    filesystems = []
    for partition in psutil.disk_partitions():
        if partition.fstype != 'squashfs':
            usage = psutil.disk_usage(partition.mountpoint)
            filesystems.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': round(usage.total / (1024**3), 2),
                'used': round(usage.used / (1024**3), 2),
                'free': round(usage.free / (1024**3), 2)
            })
    return filesystems

def get_gpu_info():
    """
    Obtém informações sobre as GPUs do sistema.
    
    Returns:
        list: Lista de dicionários contendo informações sobre cada GPU.
    """
    gpu_info = []
    try:
        # Tenta obter informações sobre GPUs NVIDIA
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            gpu_info.append({
                'gpu_id': gpu.id,
                'name': gpu.name,
                'driver_version': gpu.driver,
                'memory_total': gpu.memoryTotal if gpu.memoryTotal else 0,
                'memory_free': gpu.memoryFree if gpu.memoryFree else 0,
                'memory_used': gpu.memoryUsed if gpu.memoryUsed else 0,
                'temperature': gpu.temperature if gpu.temperature else 0
            })
        if gpu_info:
            return gpu_info
    except Exception as e:
        logging.error(f"Error retrieving NVIDIA GPU info: {e}")

    try:
        # Se não houver GPUs NVIDIA, tenta obter informações com lspci
        lspci_output = os.popen('lspci | grep -i vga').read()
        for line in lspci_output.splitlines():
            gpu_info.append({
                'gpu_id': line.split()[0],
                'name': ' '.join(line.split()[1:]),
                'driver_version': '',
                'memory_total': 0,
                'memory_free': 0,
                'memory_used': 0,
                'temperature': 0
            })
    except Exception as e:
        logging.error(f"Error retrieving GPU info using lspci: {e}")

    return gpu_info

def get_motherboard_model():
    """
    Obtém o modelo da placa-mãe a partir de arquivos do sistema.
    
    Returns:
        str: Modelo da placa-mãe, ou 'Unknown' se não puder ser obtido.
    """
    try:
        with open('/sys/class/dmi/id/board_name', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return 'Unknown'
    except Exception as e:
        logging.error(f"Error retrieving motherboard model: {e}")
        return 'Unknown'

def collect_system_info():
    """
    Coleta todas as informações do sistema.
    
    Returns:
        dict: Dicionário contendo todas as informações coletadas sobre o sistema.
    """
    system_info = {
        'hostname': socket.gethostname(),
        'linux_distribution': get_linux_distribution(),
        'kernel_version': get_kernel_version(),
        'logged_in_user': get_logged_in_user(),
        'cpu_model': get_cpu_info().get('model_name', 'Unknown'),
        'memory_total_gb': get_memory_info(),
        'uuid1': str(uuid.uuid1()),
        'collection_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_login_history': get_user_login_history(),
        'ip_and_mac_addresses': get_ip_and_mac_addresses(),
        'mounted_filesystems': get_mounted_filesystems(),
        'disk_info': get_disk_info(),
        'gpu_info': get_gpu_info(),
        'motherboard_model': get_motherboard_model()
    }
    return system_info

def save_json_to_disk(data):
    """
    Salva as informações do sistema em um arquivo JSON no disco.
    
    Args:
        data (dict): Dicionário contendo as informações do sistema a serem salvas.
    """
    filename = f"system_info_{data['uuid1']}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def send_system_info():
    """
    Coleta as informações do sistema, salva em um arquivo JSON e envia para o servidor.
    """
    system_info = collect_system_info()
    #desabilitado para não salvar o arquivo no disco
    #save_json_to_disk(system_info)
    try:
        response = requests.post('http://apps.dacom:5000/api/upload', json=system_info)
        logging.info(f"Status Code: {response.status_code}")
        logging.info(f"Response Text: {response.text}")
        try:
            logging.info(response.json())
        except ValueError:
            logging.error("Error decoding JSON response")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")

if __name__ == '__main__':
    # Instala as bibliotecas necessárias
    install_packages()
    send_system_info()
