# Używamy nowszej wersji Pythona (3.10 zamiast 3.9)
FROM python:3.10

WORKDIR /app

COPY . /app

# Najpierw aktualizujemy pip, potem instalujemy zależności
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
