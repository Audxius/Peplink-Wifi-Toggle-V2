FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir urllib3 aiohttp

COPY wifiToggle.py .

CMD ["python", "wifiToggle.py"]
