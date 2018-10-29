FROM python:3.7
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

ADD . /code
WORKDIR /code

RUN mypy --ignore-missing-imports collector_orchestrator.py 
CMD ["python", "-u", "collector_orchestrator.py"]
