ARG PYTHON_VERSION=3.9.9-slim-buster

FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  # git+https
  git \
  python3-dev \
  graphviz \
  libgraphviz-dev \
  pkg-config \
  unixodbc-dev

COPY ./images/web/requirements.txt .

RUN pip install --upgrade pip==21.3.1

# Create Python Dependency and Sub-Dependency Wheels.
RUN --mount=type=cache,target=/root/.cache \
  pip wheel --wheel-dir /usr/src/app/wheels  \
  -r requirements.txt


# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/webapp

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  libgeos-dev \
  # Logrotate and cron
  cron \
  logrotate \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/


COPY ./images/web/docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//g' /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh


COPY ./images/web/commands/ /commands
RUN sed -i 's/\r$//g' /commands/*
RUN chmod +x -R /commands


COPY ./images/web/uwsgi.ini /webapp/uwsgi.ini

COPY ./images/web/logrotate/cron /cron.txt
COPY ./images/web/logrotate/generate_configs.py /generate_configs.py

ENV UWSGI_WORKERS 4
ENV UWSGI_THREADS 1

# copy application code to WORKDIR
# COPY ./../QoS_backend ${APP_HOME}

ENTRYPOINT ["/docker-entrypoint.sh"]
