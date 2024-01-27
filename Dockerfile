# pull official base image
FROM python:3.11.2

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install psycopg2 dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc 

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

RUN NLL_DJANGO_SECRET_KEY=secret python manage.py collectstatic --no-input