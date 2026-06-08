FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service/app ./app
COPY prompts ./prompts

ENV PYTHONPATH=/app
ENV PROMPTS_DIR=/app/prompts

EXPOSE 8095

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8095"]
