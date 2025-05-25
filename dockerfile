FROM python:3.10.13-slim-bookworm


RUN apt-get update && apt-get install -y \
    sqlite3 \  
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY . .


RUN mkdir -p /app/data

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]