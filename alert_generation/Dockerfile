FROM python:3.7
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

ADD . /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/alerts"

RUN mypy --ignore-missing-imports alert_generation.py 
CMD ["python", "-u", "alert_generation.py"]
