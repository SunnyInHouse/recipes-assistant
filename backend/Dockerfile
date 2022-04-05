FROM python:3.8

WORKDIR /code

RUN pip install "poetry==1.1"

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install

WORKDIR /code/foodgram

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
