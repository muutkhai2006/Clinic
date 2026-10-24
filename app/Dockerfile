FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && addgroup --system --gid 10001 clinic \
    && adduser --system --uid 10001 --ingroup clinic --home /app clinic

COPY --chown=clinic:clinic . .

USER 10001:10001
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
