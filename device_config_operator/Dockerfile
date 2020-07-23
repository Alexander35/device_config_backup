FROM python:3.6-slim

ARG DEVICE_CONFIG_BACKUP_HOST_ADDRESS
ARG DEVICE_CONFIG_BACKUP_DB_NAME
ARG DEVICE_CONFIG_BACKUP_DB_USER_NAME
ARG DEVICE_CONFIG_BACKUP_DB_PASSWORD
ARG DEVICE_CONFIG_BACKUP_ADMIN_NAME
ARG DEVICE_CONFIG_BACKUP_ADMIN_EMAIL
ARG DEVICE_CONFIG_BACKUP_ADMIN_PASSWORD

#RUN echo "Build number: $buildno"

RUN apt-get update
RUN apt-get install -y apt-utils gcc apt-utils python3-psycopg2 libpq-dev nginx python-dev git

RUN mkdir -p /device_config_backup

WORKDIR /device_config_backup

ADD . /device_config_backup

#RUN git clone https://github.com/Alexander35/device_config_backup.git
RUN pip install --trusted-host pypi.python.org -r device_config_backup/device_config_operator/requirements.txt

RUN pip install uwsgi
RUN echo yes | python device_config_backup/manage.py collectstatic

RUN usermod -a -G www-data root

EXPOSE 8809

ENTRYPOINT ln -s /device_config_backup/device_config_backup/device_config_operator/device_config_backup_nginx.conf /etc/nginx/sites-enabled/ && rm -rf /etc/nginx/sites-enabled/default && /etc/init.d/nginx start && python device_config_backup/manage.py makemigrations --noinput && python device_config_backup/manage.py makemigrations device_config_operator --noinput && python -u device_config_backup/manage.py migrate --noinput && python -u device_config_backup/manage.py createfirstuser && uwsgi --ini /device_config_backup/device_config_backup/device_config_backup_uwsgi.ini --daemonize /device_config_backup/uwsgi.log && tail -f /dev/null
