FROM python:3.9.1-slim-buster
ENV LOG_LEVEL=DEBUG
ENV UPDATE_FREQUENCY=3600
RUN mkdir /code
WORKDIR /code
RUN apt-get update -y && \
    apt-get install git -y && \
    apt-get autoremove -y &&\
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/vishnubob/wait-for-it.git
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r ./requirements.txt
COPY . /code/
RUN pytest -v