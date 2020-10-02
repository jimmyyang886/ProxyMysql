FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
ENV LANG en_US.UTF-8 \
    LANGUAGE en_US.UTF-8

RUN apk add --no-cache curl python3 pkgconfig python3-dev openssl-dev libffi-dev musl-dev make gcc libxml2 libxslt
RUN apk add --update --no-cache g++ gcc libxslt-dev

RUN pip install pipenv

RUN mkdir -p /app/src
WORKDIR /app

ADD Pipfile /app
ADD Pipfile.lock /app

ADD Proxy_test_MP_linux.py /app/src
RUN pipenv install --system --deploy --ignore-pipfile
CMD ["python", "/app/src/Proxy_test_MP_linux.py"]
#CMD /bin/sh
