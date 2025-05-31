FROM python:latest

WORKDIR .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY req.txt req.txt

RUN pip install --no-cache-dir --upgrade -r req.txt

COPY ./src ./src

CMD ["python3", "-m", "src.rabbit_src.consumer", "consumer.py"]

CMD ["python3", "-m", "src.app.app", "app.py"]