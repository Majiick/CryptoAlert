FROM python:3.7
ARG HOST_DOCKERFILE_DIR

COPY $HOST_DOCKERFILE_DIR/requirements.txt .
COPY /common/logging/requirements.txt logging_requirements.txt
COPY /common/influxdb/requirements.txt influxdb_requirements.txt
RUN pip install -r logging_requirements.txt
RUN pip install -r influxdb_requirements.txt
RUN pip install -r requirements.txt
RUN pip install mypy

ADD $HOST_DOCKERFILE_DIR /code
COPY /common/logging/ /code
COPY /common/influxdb/ /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/alerts"
ENV PYTHONPATH "${PYTHONPATH}:/code/notifications"

RUN mypy --ignore-missing-imports *.py
RUN mypy --ignore-missing-imports ./alerts/*.py
RUN mypy --ignore-missing-imports ./notifications/*.py
CMD ["python", "-u", "alert_generation.py"]
