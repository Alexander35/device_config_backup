FROM python:3.6-slim

RUN apt-get update
RUN apt-get install -y apt-utils gcc apt-utils python3-psycopg2 libpq-dev nginx python-dev git

RUN mkdir -p /device_config_backup

WORKDIR /device_config_backup

ADD . /device_config_backup

RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN git clone https://github.com/Alexander35/device_config_backup.git
RUN rm -rf public
RUN mkdir public

RUN pip install uwsgi
RUN echo yes | python manage.py collectstatic

RUN usermod -a -G www-data root

EXPOSE 8808

ENTRYPOINT ln -s /device_config_backup/device_config_backup_nginx.conf /etc/nginx/sites-enabled/ && rm -rf /etc/nginx/sites-enabled/default && /etc/init.d/nginx start && python manage.py makemigrations --noinput && python manage.py makemigrations device_config_operator --noinput && python -u manage.py migrate --noinput && python -u manage.py createfirstuser && uwsgi --ini device_config_backup_uwsgi.ini --daemonize /device_config_backup/uwsgi.log && tail -f /dev/null
