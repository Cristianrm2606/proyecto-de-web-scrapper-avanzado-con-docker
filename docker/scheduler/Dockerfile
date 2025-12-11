FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Necesario para instalar Chromium dentro del scheduler también
RUN playwright install chromium

CMD ["python", "scheduler.py"]
