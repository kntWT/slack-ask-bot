FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
