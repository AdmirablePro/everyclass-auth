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

# install google chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb \
    && rm ./google-chrome-stable_current_amd64.deb

COPY . /var/app

# install Python dependencies
RUN pip3 install --upgrade pip \
    && pip3 install pipenv \
    && pipenv sync \
    && pip3 install uwsgitop \
    && rm -r /root/.cache

ENV UWSGI_HTTP_SOCKET ":80"

CMD ["uwsgi", "--ini", "/var/app/deploy/uwsgi.ini"]