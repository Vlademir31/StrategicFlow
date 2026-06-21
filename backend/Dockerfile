FROM python:3.11-slim

WORKDIR /app

# requirements está dentro de backend/
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# src está dentro de backend/src
COPY backend/src ./src

# frontend está na raiz do contexto
COPY frontend ./frontend

CMD ["python", "src/api.py"]