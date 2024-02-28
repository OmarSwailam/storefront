FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Required to install mysqlclient with Pip
RUN apt-get update \
  && apt-get install python3-dev default-libmysqlclient-dev gcc -y

# Install application dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the application files into the image
COPY . /app/

# Expose port 8000 on the container
EXPOSE 8000