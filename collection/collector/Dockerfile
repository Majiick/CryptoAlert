FROM python:3.7
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

COPY . /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/data_api"

RUN mypy --ignore-missing-imports collector_starter.py
CMD ["python", "-u", "collector_starter.py"]
# RUN mypy --ignore-missing-imports data_api/data_source.py
# CMD ["python", "-u", "data_api/data_source.py"]
