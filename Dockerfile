FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# Instale dependências do sistema necessárias para compilar o cryptography
RUN apt-get update && apt-get install -y \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-dev \
  gcc \
  && pip install --no-cache-dir -r requirements.txt \
  && apt-get remove -y gcc build-essential \
  && apt-get autoremove -y \
  && apt-get clean

COPY app.py .
COPY templates/ templates/

EXPOSE 5000

CMD ["python", "app.py"]
