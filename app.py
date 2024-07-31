from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import json

# Cria uma aplicação Flask
app = Flask(__name__)

# Configura a URI do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///system_info.db'

# Inicializa o objeto SQLAlchemy
db = SQLAlchemy(app)

# Definição das tabelas do banco de dados usando SQLAlchemy ORM

class SystemInfo(db.Model):
    """
    Model para armazenar informações do sistema.
    """
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(120), nullable=False)
    linux_distribution = db.Column(db.String(120), nullable=False)
    kernel_version = db.Column(db.String(120), nullable=False)
    logged_in_user = db.Column(db.String(120), nullable=False)
    cpu_model = db.Column(db.String(120), nullable=False)
    memory_total_gb = db.Column(db.Float, nullable=False)
    uuid1 = db.Column(db.String(36), unique=True, nullable=False)
    collection_datetime = db.Column(db.String(120), nullable=False)
    motherboard_model = db.Column(db.String(255))

    # Relacionamentos
    user_login_history = db.relationship('UserLoginHistory', backref='system_info', lazy=True)
    ip_and_mac_addresses = db.relationship('IPAndMacAddress', backref='system_info', lazy=True)
    mounted_filesystems = db.relationship('MountedFilesystems', backref='system_info', lazy=True)
    disk_info = db.relationship('DiskInfo', backref='system_info', uselist=False)
    gpu_info = db.relationship('GPUInfo', backref='system_info', lazy=True)

class UserLoginHistory(db.Model):
    """
    Model para armazenar o histórico de login de usuários.
    """
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(120), nullable=False)
    tty = db.Column(db.String(120), nullable=False)
    ip = db.Column(db.String(120), nullable=False)
    datetime = db.Column(db.String(120), nullable=False)
    system_info_id = db.Column(db.Integer, db.ForeignKey('system_info.id'), nullable=False)

class IPAndMacAddress(db.Model):
    """
    Model para armazenar informações de IP e MAC Address.
    """
    id = db.Column(db.Integer, primary_key=True)
    interface = db.Column(db.String(120), nullable=False)
    ip = db.Column(db.String(120), nullable=False)
    mac = db.Column(db.String(120), nullable=False)
    system_info_id = db.Column(db.Integer, db.ForeignKey('system_info.id'), nullable=False)

class MountedFilesystems(db.Model):
    """
    Model para armazenar informações de sistemas de arquivos montados.
    """
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(120), nullable=False)
    mountpoint = db.Column(db.String(120), nullable=False)
    fstype = db.Column(db.String(120), nullable=False)
    total = db.Column(db.Float, nullable=False)
    used = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    system_info_id = db.Column(db.Integer, db.ForeignKey('system_info.id'), nullable=False)

class DiskInfo(db.Model):
    """
    Model para armazenar informações de disco.
    """
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    free = db.Column(db.Float, nullable=False)
    system_info_id = db.Column(db.Integer, db.ForeignKey('system_info.id'), nullable=False)

class GPUInfo(db.Model):
    """
    Model para armazenar informações da placa de vídeo.
    """
    id = db.Column(db.Integer, primary_key=True)
    gpu_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    driver_version = db.Column(db.String(120), nullable=False)
    memory_total = db.Column(db.Float, nullable=False)
    memory_free = db.Column(db.Float, nullable=False)
    memory_used = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    system_info_id = db.Column(db.Integer, db.ForeignKey('system_info.id'), nullable=False)


def create_tables():
    """
    Função para criar as tabelas no banco de dados.
    """
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    """
    Rota para a página inicial que lista todas as informações do sistema.
    """
    system_infos = SystemInfo.query.all()
    return render_template('index.html', system_infos=system_infos)

@app.route('/details/<int:id>')
def details(id):
    """
    Rota para exibir os detalhes de uma informação do sistema específica.
    """
    system_info = SystemInfo.query.get_or_404(id)
    return render_template('details.html', system_info=system_info)

@app.route('/api/upload', methods=['POST'])
def upload():
    """
    Rota API para upload de informações do sistema via JSON.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Salvar informações do sistema
    system_info = SystemInfo(
        hostname=data.get('hostname'),
        linux_distribution=json.dumps(data.get('linux_distribution')),  # Convertendo para string JSON
        kernel_version=data.get('kernel_version'),
        logged_in_user=data.get('logged_in_user'),
        cpu_model=data.get('cpu_model'),
        memory_total_gb=data.get('memory_total_gb'),
        uuid1=data.get('uuid1'),
        collection_datetime=data.get('collection_datetime'),
        motherboard_model=data['motherboard_model']
    )
    
    db.session.add(system_info)
    db.session.commit()
    
    # Salvar dados relacionados
    user_login_history = data.get('user_login_history', [])
    ip_and_mac_addresses = data.get('ip_and_mac_addresses', [])
    mounted_filesystems = data.get('mounted_filesystems', [])
    disk_info = data.get('disk_info', {})
    gpu_info = data.get('gpu_info', [])

    for entry in user_login_history:
        login_history = UserLoginHistory(
            user=entry['user'],
            tty=entry['tty'],
            ip=entry['ip'],
            datetime=entry['datetime'],
            system_info_id=system_info.id
        )
        db.session.add(login_history)

    for entry in ip_and_mac_addresses:
        ip_mac = IPAndMacAddress(
            interface=entry['interface'],
            ip=entry['ip'],
            mac=entry['mac'],
            system_info_id=system_info.id
        )
        db.session.add(ip_mac)
    
    for entry in mounted_filesystems:
        filesystem = MountedFilesystems(
            device=entry['device'],
            mountpoint=entry['mountpoint'],
            fstype=entry['fstype'],
            total=entry['total'],
            used=entry['used'],
            free=entry['free'],
            system_info_id=system_info.id
        )
        db.session.add(filesystem)

    if disk_info:
        disk = DiskInfo(
            total=disk_info.get('total'),
            free=disk_info.get('free'),
            system_info_id=system_info.id
        )
        db.session.add(disk)

    for entry in gpu_info:
        gpu = GPUInfo(
            gpu_id=entry['gpu_id'],  # Corrigido para corresponder ao nome do campo no modelo
            name=entry['name'],
            driver_version=entry['driver_version'],
            memory_total=entry['memory_total'],
            memory_free=entry['memory_free'],
            memory_used=entry['memory_used'],
            temperature=entry['temperature'],
            system_info_id=system_info.id
        )
        db.session.add(gpu)

    try:
        db.session.commit()
        return jsonify({'message': 'Data saved successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    create_tables()  # Garante que as tabelas são criadas
    app.run(host='0.0.0.0', port=5000, debug=True)
