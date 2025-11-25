# This is the Dockerfile (Not the compose file!)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg git

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir flask flask-cors
RUN pip install --no-cache-dir https://github.com/yt-dlp/yt-dlp/archive/master.zip

COPY api.py .
RUN mkdir -p /app/downloads

CMD ["python", "api.py"]
