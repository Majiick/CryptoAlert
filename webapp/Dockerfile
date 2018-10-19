FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install mypy

# ENV FLASK_APP webapp.py
# EXPOSE 4000/tcp
RUN mypy --ignore-missing-imports webapp.py
CMD ["gunicorn", "-w", "1", "-b", "unix:/run/gunicorn.sock", "webapp:app"]
# CMD ["python", "-m", "flask", "run"]
