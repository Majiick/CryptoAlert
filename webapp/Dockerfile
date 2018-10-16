FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

ENV FLASK_APP webapp.py
CMD ["python", "-m", "flask", "run"]
