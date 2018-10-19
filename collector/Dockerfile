FROM python:3.7
ADD . /code
WORKDIR /code
ADD . ../common/mypycheckandrun.sh
RUN pip install -r requirements.txt
RUN pip install mypy

# RUN mypy --ignore-missing-imports collector.py
# CMD ["python", "-u", "collector.py"]
RUN mypy --ignore-missing-imports data_api/data_source.py
CMD ["python", "-u", "data_api/data_source.py"]
