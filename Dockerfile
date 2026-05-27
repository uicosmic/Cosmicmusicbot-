FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y ffmpeg git python3-dev build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
