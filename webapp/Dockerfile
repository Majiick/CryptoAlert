FROM python:3.7
ARG HOST_DOCKERFILE_DIR

# Install NPM
RUN apt-get update
RUN apt-get install --yes curl
RUN curl -sL https://deb.nodesource.com/setup_11.x | bash
RUN apt-get install --yes nodejs
RUN npm -v

RUN mkdir code
RUN mkdir code/static
WORKDIR /code/static
ADD $HOST_DOCKERFILE_DIR/static/package.json /code/static
RUN mkdir node_modules; exit 0  # Make node_modules so the install installs in this folder. Exit 0 is needed if node_modules already exist
RUN npm install
ADD $HOST_DOCKERFILE_DIR /code
RUN npm run-script build


WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install mypy


WORKDIR /code

# ENV FLASK_APP webapp.py
# EXPOSE 4000/tcp
# Python buffered so Gunicorn python prints
ENV PYTHONUNBUFFERED=0
RUN mypy --ignore-missing-imports webapp.py
# Stdio inheritance so that gunicorn python prints
CMD ["gunicorn", "-w", "1", "--enable-stdio-inheritance", "-b", "unix:/run/gunicorn.sock", "webapp:app"]
# CMD ["python", "-m", "flask", "run"]
