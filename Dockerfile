FROM python:3.13-alpine

# Install build dependencies and common libraries needed for Python packages
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    python3-dev \
    musl-dev \
    linux-headers \
    git

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

ENV FLASK_APP=run.py

CMD ["flask", "run"]
