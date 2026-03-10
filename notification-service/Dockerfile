FROM python:3.12-slim

WORKDIR /app

COPY ./notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./shared /shared
ENV PYTHONPATH=/

COPY ./notification-service /app

CMD ["python", "main.py"]
