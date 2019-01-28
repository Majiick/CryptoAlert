FROM python:3.7
ARG HOST_DOCKERFILE_DIR

COPY $HOST_DOCKERFILE_DIR/requirements.txt .
COPY $HOST_DOCKERFILE_DIR/collector/requirements.txt collector_requirements.txt
COPY /common/logging/requirements.txt logging_requirements.txt
RUN pip install -r logging_requirements.txt
RUN pip install -r requirements.txt
RUN pip install -r collector_requirements.txt
RUN pip install mypy

ADD $HOST_DOCKERFILE_DIR /code
COPY /common/logging/ /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/collector"
ENV PYTHONPATH "${PYTHONPATH}:/code/collector/data_api"

RUN mypy --ignore-missing-imports collector_orchestrator.py 
CMD ["python", "-u", "collector_orchestrator.py"]
