FROM python:3.7
ARG HOST_DOCKERFILE_DIR

COPY $HOST_DOCKERFILE_DIR/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

ADD $HOST_DOCKERFILE_DIR /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/alerts"

RUN mypy --ignore-missing-imports alert_generation.py 
CMD ["python", "-u", "alert_generation.py"]
