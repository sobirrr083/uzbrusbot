FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Token o'rniga standart qiymat (real tokenni Docker run paytida --env bilan yuboriladi)
ENV TELEGRAM_TOKEN=your_token_here

CMD ["python", "main.py"]
