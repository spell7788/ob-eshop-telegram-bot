FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

ENV PIP_NO_CACHE_DIR false

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN apk --no-cache add --virtual build-dependencies \
    python3-dev openssl-dev libffi-dev build-base gcc \
    && pip install pipenv \
    && pipenv install --deploy --system \
    && pip uninstall pipenv -y \
    && apk del build-dependencies

COPY . /app

CMD ["python", "-m", "bot"]
