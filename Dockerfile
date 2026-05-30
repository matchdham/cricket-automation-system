FROM python:3.11-slim

WORKDIR /app

# Copy saari files main area mein
COPY . .

# Dependencies install karo
RUN pip install --no-cache-dir -r requirements.txt

# SYSTEM PATH FIX: Yeh line Python ko poore project (root) se modules dhoondhne degi
ENV PYTHONPATH=/app

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

EXPOSE 8000

# App ko root level se run karo taaki use config.py mil sake
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "60", "backend.app:app"]

