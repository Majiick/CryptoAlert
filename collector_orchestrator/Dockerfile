FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install mypy

RUN mypy --ignore-missing-imports collector_orchestrator.py 
CMD ["python", "-u", "collector_orchestrator.py"]
