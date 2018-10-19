FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

CMD ["python", "-u", "collector.py"]
# CMD ["python", "-u", "data_api/data_sources_config.py"]
