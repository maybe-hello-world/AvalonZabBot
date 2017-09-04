FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py bot.py

CMD ["python", "./bot.py"]