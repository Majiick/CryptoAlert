FROM python:3.7
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

COPY . /code
WORKDIR /code

# RUN mypy --ignore-missing-imports collector.py
# CMD ["python", "-u", "collector.py"]
RUN mypy --ignore-missing-imports data_api/data_source.py
CMD ["python", "-u", "data_api/data_source.py"]
