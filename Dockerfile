# Use uma imagem base com Python 3.10
FROM python:3.10-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código da aplicação para o diretório de trabalho no container
COPY app.py .
COPY templates/ templates/

# Exponha a porta 5000 para acesso externo
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python", "app.py"]
