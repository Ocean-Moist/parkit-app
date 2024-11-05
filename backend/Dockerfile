FROM python:3.11-slim

RUN python -m venv /opt/venv
RUN apt-get update && apt-get install libsm6 libxext6 ffmpeg -y
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY yolov8n.pt .
COPY app/ .
ENV PATH="/opt/venv/bin:$PATH"
ENV HOME=/tmp

ENV APP_MODULE=main:app
ENV PORT=5000

USER 1000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5000", "main:app"]
EXPOSE 5000

