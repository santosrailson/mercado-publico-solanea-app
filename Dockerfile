FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

RUN mkdir -p /data

ENV DB_PATH=/data/mercado.db
ENV SECRET_KEY=solanea_mp_secret_2026_change_in_prod
ENV PYTHONPATH=/app/backend

EXPOSE 8002

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8002"]
