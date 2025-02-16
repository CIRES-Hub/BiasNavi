FROM python:3.10.12-slim
WORKDIR /home/sandbox
COPY requirements.txt ./
RUN apt-get update && apt-get install build-essential -y
RUN pip install --no-cache-dir -r requirements.txt