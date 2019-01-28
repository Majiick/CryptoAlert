FROM python:3.7
ARG HOST_DOCKERFILE_DIR

COPY $HOST_DOCKERFILE_DIR/requirements.txt .
COPY /common/logging/requirements.txt logging_requirements.txt
RUN pip install -r logging_requirements.txt
RUN pip install -r requirements.txt
RUN pip install mypy

ADD $HOST_DOCKERFILE_DIR /code
COPY /common/logging/ /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"

RUN mypy --ignore-missing-imports socketio_server.py 
CMD ["python", "-u", "socketio_server.py"]
