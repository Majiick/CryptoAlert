FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

# ENV FLASK_APP webapp.py
# EXPOSE 4000/tcp
CMD ["gunicorn", "-w", "1", "-b", "unix:/run/gunicorn.sock", "webapp:app"]
# CMD ["python", "-m", "flask", "run"]
