FROM python:3.4

MAINTAINER Minh-Long Do <minhlong.langos@gmail>

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .


EXPOSE 8000

CMD ["gunicorn", "codemetric.wsgi", "-b", "0.0.0.0:8000"]
