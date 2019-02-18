FROM python:3.7.1-slim-stretch
LABEL maintainer="frederic.t.chan@gmail.com"
ENV REFRESHED_AT 20181218
ENV MODE PRODUCTION
ENV FLASK_ENV production
ENV PIPENV_VENV_IN_PROJECT 1

WORKDIR /var/app

# Why we need these packages?
# - procps contains useful proccess control commands like: free, kill, pkill, ps, top
# - wget is quite basic tool
# - git for using git in our app
# - gcc, libpcre3-dev for compiling uWSGI
# - libffi-dev for installing Python package cffi
# - libssl-dev for installing Python package cryptography
# - chromedriver for selenium
RUN apt-get update \
    && apt-get install -y procps wget gcc libpcre3-dev git libffi-dev libssl-dev chromedriver\
    && pip install uwsgi

# install gor
RUN cd / \
    && mkdir gor \
    && cd gor \
    && wget https://github.com/buger/goreplay/releases/download/v0.16.1/gor_0.16.1_x64.tar.gz \
    && tar xzf gor_0.16.1_x64.tar.gz \
    && rm gor_0.16.1_x64.tar.gz

COPY . /var/app

# install Python dependencies
RUN pip3 install --upgrade pip \
    && pip3 install pipenv \
    && pipenv sync \
    && pip3 install uwsgitop \
    && rm -r /root/.cache

ENV UWSGI_HTTP_SOCKET ":80"

CMD ["bash", "deploy/docker-cmd.sh"]