# Simple production container
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p uploads

EXPOSE 5000
ENV PORT=5000

# Use Gunicorn in containers
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
