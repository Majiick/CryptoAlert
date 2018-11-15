FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install mypy


# Install NPM
RUN apt-get update
RUN apt-get install --yes curl
RUN curl -sL https://deb.nodesource.com/setup_11.x | bash
RUN apt-get install --yes nodejs
RUN npm -v

WORKDIR /code/static
RUN mkdir node_modules; exit 0  # Make node_modules so the install installs in this folder. Exit 0 is needed if node_modules already exist
RUN npm install
RUN npm run-script build

WORKDIR /code

# ENV FLASK_APP webapp.py
# EXPOSE 4000/tcp
RUN mypy --ignore-missing-imports webapp.py
CMD ["gunicorn", "-w", "1", "-b", "unix:/run/gunicorn.sock", "webapp:app"]
# CMD ["python", "-m", "flask", "run"]
