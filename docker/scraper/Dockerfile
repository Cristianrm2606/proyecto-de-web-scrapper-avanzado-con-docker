FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Instalar únicamente Chromium con dependencias
RUN playwright install --with-deps chromium

COPY . .

CMD ["python", "main.py"]
