FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Render supplies PORT and RENDER_EXTERNAL_URL automatically; retain a local fallback.
ENV PYTHONUNBUFFERED=1 PREVIEW_MODE=false DATA_DIR=/data
EXPOSE 10000
CMD ["sh", "-c", "exec python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1 --no-access-log"]
