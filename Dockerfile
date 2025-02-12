# syntax=docker/dockerfile:1
FROM python:3.11.1

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install --upgrade pip

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY posts /code/posts
COPY spotify /code/spotify
COPY users /code/users
COPY vynle /code/vynle
COPY vynle_app /code/vynle_app
COPY manage.py /code/manage.py
