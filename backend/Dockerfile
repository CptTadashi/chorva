# Python bazasini tanlaymiz
FROM python:3.11-slim

# Ishchi katalogni belgilaymiz
WORKDIR /app

# Kerakli paketlarni o'rnatamiz (PostgreSQL uchun build-essential kerak bo'lishi mumkin)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Talablarni nusxalaymiz va o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodni nusxalaymiz
COPY . .

# Media papkasini yaratib qo'yamiz
RUN mkdir -p media

# Portni ochamiz
EXPOSE 8000

# Standart buyruq (Lekin docker-compose orqali o'zgartiriladi)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
