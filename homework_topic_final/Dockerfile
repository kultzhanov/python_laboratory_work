FROM python:3.12-slim

LABEL maintainer="Kultzhanov Maksim"
LABEL description="Task Manager API Server"

WORKDIR /app

COPY src/ ./src/
COPY main.py .
COPY config.yml .

RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "main.py"]
