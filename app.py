from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import or_, and_, not_
from datetime import datetime

# Cria uma aplicação Flask
app = Flask(__name__)

# Configura a URI do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///system_info.db'
app.config['SQLALCHEMY_BINDS'] = {
    'logs': 'mysql+pymysql://root:root@172.16.255.209:3306/dacomlogs'
}

# Inicializa o objeto SQLAlchemy
db = SQLAlchemy(app)

# Inicializa o objeto Migrate
migrate = Migrate(app, db)

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
    patrimony = db.Column(db.String(50), nullable=True)

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
    
    
class SystemEvents(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'SystemEvents'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CustomerID = db.Column(db.Integer)
    ReceivedAt = db.Column(db.DateTime)
    DeviceReportedTime = db.Column(db.DateTime)
    Facility = db.Column(db.SmallInteger)
    Priority = db.Column(db.SmallInteger)
    FromHost = db.Column(db.String(60))
    Message = db.Column(db.Text)
    NTSeverity = db.Column(db.Integer)
    Importance = db.Column(db.Integer)
    EventSource = db.Column(db.String(60))
    EventUser = db.Column(db.String(60))
    EventCategory = db.Column(db.Integer)
    EventID = db.Column(db.Integer)
    EventBinaryData = db.Column(db.Text)
    MaxAvailable = db.Column(db.Integer)
    CurrUsage = db.Column(db.Integer)
    MinUsage = db.Column(db.Integer)
    MaxUsage = db.Column(db.Integer)
    InfoUnitID = db.Column(db.Integer)
    SysLogTag = db.Column(db.String(60))
    EventLogType = db.Column(db.String(60))
    GenericFileName = db.Column(db.String(60))
    SystemID = db.Column(db.Integer)

    properties = db.relationship('SystemEventsProperties', backref='event', lazy=True)


class SystemEventsProperties(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'SystemEventsProperties'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SystemEventID = db.Column(db.Integer, db.ForeignKey('SystemEvents.ID', ondelete="CASCADE"))
    ParamName = db.Column(db.String(255))
    ParamValue = db.Column(db.Text)

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
    room = request.args.get('room')
    specific_rooms = ["e003", "e006", "e007", "e100", "e101", "e102", "e103", "e104", "e105"]
    if room:
        if room in specific_rooms:
            system_infos = SystemInfo.query.filter(SystemInfo.hostname.like(f'%{room}')).all()
        elif room == "dacom":
            system_infos = SystemInfo.query.filter(
                and_(*[SystemInfo.hostname.notlike(f'%{r}') for r in specific_rooms])
            ).all()
        else:
            system_infos = []
    else:
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
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Extrai a parte do UUID após o último '-'
    new_uuid_suffix = data['uuid1'].rsplit('-', 1)[1]

    # Verifica se um registro com o mesmo hostname ou UUID sufixo existe
    existing_record = SystemInfo.query.filter(
        or_(
            SystemInfo.hostname == data['hostname'],
            SystemInfo.uuid1.like(f'%{new_uuid_suffix}')
        )
    ).first()

    if existing_record:
        # Atualiza o registro existente
        existing_record.linux_distribution = data.get('linux_distribution')
        existing_record.kernel_version = data.get('kernel_version')
        existing_record.logged_in_user = data.get('logged_in_user')
        existing_record.cpu_model = data.get('cpu_model')
        existing_record.memory_total_gb = data.get('memory_total_gb')
        existing_record.collection_datetime = data.get('collection_datetime')
        existing_record.motherboard_model = data.get('motherboard_model')
        existing_record.patrimony = data.get('patrimony')
        db.session.commit()
        return jsonify({'message': 'Data updated successfully'}), 200

    # Se nenhum registro correspondente for encontrado, insere um novo registro
    system_info = SystemInfo(
        hostname=data.get('hostname'),
        linux_distribution=data.get('linux_distribution'),
        kernel_version=data.get('kernel_version'),
        logged_in_user=data.get('logged_in_user'),
        cpu_model=data.get('cpu_model'),
        memory_total_gb=data.get('memory_total_gb'),
        uuid1=data.get('uuid1'),
        collection_datetime=data.get('collection_datetime'),
        motherboard_model=data.get('motherboard_model'),
        patrimony=data.get('patrimony')  # Incluído o campo patrimony
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
    
@app.route('/api/logs/machine/<int:machine_id>')
def api_logs_by_machine(machine_id):
    machine = SystemInfo.query.get_or_404(machine_id)
    hostname = machine.hostname

    logs = SystemEvents.query.filter(SystemEvents.FromHost == hostname)\
        .order_by(SystemEvents.ReceivedAt.desc())\
        .limit(100).all()

    return jsonify([
        {
            "id": log.ID,
            "received_at": log.ReceivedAt.isoformat(),
            "from_host": log.FromHost,
            "message": log.Message,
            "event_source": log.EventSource,
            "event_user": log.EventUser,
            "event_log_type": log.EventLogType,
        }
        for log in logs
    ])


@app.route('/logs/machine/<int:machine_id>')
def logs_by_machine(machine_id):
    machine = SystemInfo.query.get_or_404(machine_id)
    hostname = machine.hostname

    logs = SystemEvents.query.filter(SystemEvents.FromHost == hostname)\
        .order_by(SystemEvents.ReceivedAt.desc())\
        .limit(100).all()
        
    # Captura o intervalo da URL (padrão 10s se não definido)
    interval = int(request.args.get('interval', 10))

    return render_template("logs.html", logs=logs, machine_id=machine_id, hostname=hostname, interval=interval)



if __name__ == '__main__':
    create_tables()  # Garante que as tabelas são criadas
    app.run(host='0.0.0.0', port=5000, debug=True)
