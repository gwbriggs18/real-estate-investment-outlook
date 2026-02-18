# Investment Outlook – stock & real estate hypothetical returns (Python backend)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY backend ./backend
COPY frontend ./frontend

ENV PYTHONUNBUFFERED=1
EXPOSE 3000

# API key must be provided at runtime via env or docker-compose
CMD ["python", "app.py"]
