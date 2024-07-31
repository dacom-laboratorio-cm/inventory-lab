import os
import platform
import psutil
import socket
import json
import uuid
import requests
import distro
import GPUtil
from datetime import datetime

def get_linux_distribution():
    return distro.name(), distro.version()

def get_kernel_version():
    return platform.release()

def get_logged_in_user():
    return os.getlogin()

def get_user_login_history():
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
    mem_info = psutil.virtual_memory()
    return round(mem_info.total / (1024**3), 2)

def get_disk_info():
    disk_info = psutil.disk_usage('/')
    return {
        'total': round(disk_info.total / (1024**3), 2),
        'free': round(disk_info.free / (1024**3), 2)
    }

def get_mounted_filesystems():
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
    gpu_info = []
    try:
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
        print(f"Error retrieving NVIDIA GPU info: {e}")

    try:
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
        print(f"Error retrieving GPU info using lspci: {e}")

    return gpu_info

def get_motherboard_model():
    """
    Retorna o modelo da placa-mãe a partir de arquivos do sistema.
    """
    try:
        with open('/sys/class/dmi/id/board_name', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return 'Unknown'
    except Exception as e:
        print(f"Error retrieving motherboard model: {e}")
        return 'Unknown'

def collect_system_info():
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
    filename = f"system_info_{data['uuid1']}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def send_system_info():
    system_info = collect_system_info()
    save_json_to_disk(system_info)
    try:
        response = requests.post('http://192.168.2.61:5000/api/upload', json=system_info)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        try:
            print(response.json())
        except ValueError:
            print("Error decoding JSON response")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    send_system_info()
