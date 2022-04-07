FROM python:3.8

WORKDIR /code

RUN pip install "poetry==1.1"

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry config virtualenvs.create false
RUN poetry install

COPY /foodgram /code/
COPY .env /code/

WORKDIR /code

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
