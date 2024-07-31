import os
import platform
import psutil
import socket
import json
import uuid
import requests
import distro
from datetime import datetime

def get_linux_distribution():
    """
    Retorna a distribuição Linux e sua versão.
    """
    return distro.name(), distro.version()

def get_kernel_version():
    """
    Retorna a versão do kernel do sistema operacional.
    """
    return platform.release()

def get_logged_in_user():
    """
    Retorna o usuário atualmente logado no sistema.
    """
    return os.getlogin()

def get_user_login_history():
    """
    Retorna o histórico de login dos usuários.
    Utiliza o comando 'last -F' para obter os logins.
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
    # Remove duplicatas e mantém apenas o último login de cada usuário
    latest_logins = {}
    for entry in login_history:
        latest_logins[entry['user']] = entry
    return list(latest_logins.values())

def get_ip_and_mac_addresses():
    """
    Retorna os endereços IP e MAC das interfaces de rede.
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
    Retorna informações sobre a CPU do sistema.
    """
    cpu_info = {}
    with open('/proc/cpuinfo') as f:
        for line in f:
            if 'model name' in line or 'Nome do modelo' in line:
                cpu_info['model_name'] = line.split(':')[1].strip()
                break
    return cpu_info

def get_memory_info():
    """
    Retorna a quantidade total de memória RAM do sistema em GB.
    """
    mem_info = psutil.virtual_memory()
    return round(mem_info.total / (1024**3), 2)  # Converte para GB e arredonda para 2 casas decimais

def get_disk_info():
    """
    Retorna informações sobre o disco do sistema.
    """
    disk_info = psutil.disk_usage('/')
    return {
        'total': round(disk_info.total / (1024**3), 2),  # Converte para GB e arredonda para 2 casas decimais
        'free': round(disk_info.free / (1024**3), 2)    # Converte para GB e arredonda para 2 casas decimais
    }

def get_mounted_filesystems():
    """
    Retorna informações sobre os sistemas de arquivos montados.
    """
    filesystems = []
    for partition in psutil.disk_partitions():
        if partition.fstype != 'squashfs':
            usage = psutil.disk_usage(partition.mountpoint)
            filesystems.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': round(usage.total / (1024**3), 2),  # Converte para GB e arredonda para 2 casas decimais
                'used': round(usage.used / (1024**3), 2),    # Converte para GB e arredonda para 2 casas decimais
                'free': round(usage.free / (1024**3), 2)     # Converte para GB e arredonda para 2 casas decimais
            })
    return filesystems

def collect_system_info():
    """
    Coleta todas as informações do sistema e retorna como um dicionário.
    """
    system_info = {
        'hostname': socket.gethostname(),
        'linux_distribution': get_linux_distribution(),
        'kernel_version': get_kernel_version(),
        'logged_in_user': get_logged_in_user(),
        'cpu_model': get_cpu_info()['model_name'],
        'memory_total_gb': get_memory_info(),
        'uuid1': str(uuid.uuid1()),
        'collection_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_login_history': get_user_login_history(),
        'ip_and_mac_addresses': get_ip_and_mac_addresses(),
        'mounted_filesystems': get_mounted_filesystems(),
        'disk_info': get_disk_info()
    }
    return system_info

def save_json_to_disk(data):
    """
    Salva os dados coletados em um arquivo JSON no disco.
    """
    filename = f"{data['uuid1']}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def send_system_info():
    """
    Coleta as informações do sistema, salva em disco e envia para o servidor.
    """
    system_info = collect_system_info()
    save_json_to_disk(system_info)
    response = requests.post('http://192.168.2.61:5000/api/upload', json=system_info)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    try:
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("Error decoding JSON response")

if __name__ == '__main__':
    send_system_info()
