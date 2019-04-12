# CryptoAlert
# Files
All of the files are written by me except for the configuration files for grafana, nginx and graylog.

# How to run
Clone the repo, run docker-compose build & docker-compose run in the Graylog directory. The Graylog config might have to be configured with the right external IP to work.

Then run docker-compose build & docker-compose run in the root directory. The web server should spin up and be accessible on port 80 externally on the IP of the server.
