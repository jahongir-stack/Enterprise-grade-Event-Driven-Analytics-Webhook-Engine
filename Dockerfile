FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY event_engine/ ./event_engine/

EXPOSE 8000

CMD ["uvicorn", "event_engine.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
