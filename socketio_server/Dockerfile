FROM python:3.7
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mypy

ADD . /code
WORKDIR /code
ENV PYTHONPATH "${PYTHONPATH}:/code"

RUN mypy --ignore-missing-imports socketio_server.py 
CMD ["python", "-u", "socketio_server.py"]
