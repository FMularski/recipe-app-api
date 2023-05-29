FROM python:3.9-alpine3.13

# maintainer of the image
LABEL maintainer="mularskif@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/requirements.txt
COPY requirements.dev.txt /tmp/requirements.dev.txt

COPY ./app /app

WORKDIR /app

EXPOSE 8000

# arg to tell if should install dev dependencies, default false but overwritten in compose
ARG DEV=false

# * create python virutal environment to make sure no already installed dependencies
# clash with project dependenciec
# * remove tmp dir when no longer needed
# * create a new user in the system
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# add path to executables
ENV PATH="/py/bin:$PATH"

# switch from root to the newly created user (never use the root user!) 
USER django-user