FROM python:3.6-slim

ARG DEVICE_CONFIG_BACKUP_HOST_ADDRESS
ARG DEVICE_CONFIG_BACKUP_DB_NAME
ARG DEVICE_CONFIG_BACKUP_DB_USER_NAME
ARG DEVICE_CONFIG_BACKUP_DB_PASSWORD
ARG DEVICE_CONFIG_BACKUP_ADMIN_NAME
ARG DEVICE_CONFIG_BACKUP_ADMIN_EMAIL
ARG DEVICE_CONFIG_BACKUP_ADMIN_PASSWORD

ARG RMQ_PING_OPERATOR_RMQ_QUEUE_IN
ARG MQ_TELNET_OPERATOR_REDIRECT_TO_QUEUE
ARG RMQ_TELNET_OPERATOR_RMQ_EXCHANGE
ARG RMQ_TELNET_OPERATOR_RMQ_QUEUE_IN
ARG RMQ_TELNET_OPERATOR_REDIRECT_TO_EXCHANGE
ARG RMQ_PING_COMMANDER_RMQ_EXCHANGE
ARG RMQ_HOST
ARG POSTGRES_COMMANDER_RMQ_EXCHANGE
ARG POSTGRES_COMMANDER_RMQ_QUEUE_IN
ARG EASY_CROSSING_POST_ADDRESS

RUN apt-get update
RUN apt-get install -y apt-utils gcc apt-utils python3-psycopg2 libpq-dev nginx python-dev git

RUN mkdir -p /device_config_backup

WORKDIR /device_config_backup

ADD . /device_config_backup

RUN pip install --trusted-host pypi.python.org -r device_config_operator/requirements.txt

RUN pip install uwsgi
RUN echo yes | python manage.py collectstatic

RUN usermod -a -G www-data root

EXPOSE 8809

ENTRYPOINT ln -s /tmp/device_config_backup/device_config_operator/device_config_backup_nginx.conf /etc/nginx/sites-enabled/ && rm -rf /etc/nginx/sites-enabled/default && /etc/init.d/nginx start && python manage.py makemigrations --noinput && python manage.py makemigrations device_config_operator --noinput && python -u manage.py migrate --noinput && python -u manage.py createfirstuser && uwsgi --ini /tmp/device_config_operator/device_config_backup_uwsgi.ini --daemonize uwsgi.log && tail -f /dev/null
