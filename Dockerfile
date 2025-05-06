FROM python:slim

RUN python -m venv /venv

ENV PATH="/venv/bin:$PATH"

RUN pip install bottle gunicorn

COPY src /src
COPY static /static

WORKDIR /src

CMD gunicorn --bind :8888 app:app
