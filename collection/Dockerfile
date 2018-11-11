FROM python:3.7
COPY ./requirements.txt .
COPY ./collector/requirements.txt collector_requirements.txt
RUN pip install -r requirements.txt
RUN pip install -r collector_requirements.txt
RUN pip install mypy

ADD . /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/collector"
ENV PYTHONPATH "${PYTHONPATH}:/code/collector/data_api"

RUN mypy --ignore-missing-imports collector_orchestrator.py 
CMD ["python", "-u", "collector_orchestrator.py"]