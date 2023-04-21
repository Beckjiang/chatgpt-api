FROM python:3.11-alpine3.16

WORKDIR /app

COPY . ./

RUN rm config/*

RUN pip install -r requirements.txt

CMD [ "python", "app.py"]