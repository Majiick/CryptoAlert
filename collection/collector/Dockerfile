FROM python:3.7
ARG HOST_DOCKERFILE_DIR

COPY $HOST_DOCKERFILE_DIR/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

COPY $HOST_DOCKERFILE_DIR /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/data_api"

RUN mypy --ignore-missing-imports collector_starter.py
CMD ["python", "-u", "collector_starter.py"]
# RUN mypy --ignore-missing-imports data_api/data_source.py
# CMD ["python", "-u", "data_api/data_source.py"]
