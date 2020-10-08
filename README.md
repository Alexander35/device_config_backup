# Как развернуть device_config_backup на сервере
Рекомендуется использовать на сервере и на контрольном хосте Debian 10

## Установить на сервере (выполняется один раз при смене сервера)

### 1. postgresql

Установливаем
``` sudo apt-get install postgresql ```

Создаём пользователя  device_config_backup и БД device_config_backup
``` sudo su postgres ```
``` psql ```
``` CREATE USER device_config_backup; ```
``` ALTER USER device_config_backup PASSWORD 'device_config_backup'; ```
``` CREATE DATABASE device_config_backup; ```
``` GRANT ALL ON DATABASE device_config_backup TO device_config_backup; ```

Разрешаем устанавливать соединение с базой от любого адреса для контейнера 
В файле
``` /etc/postgresql/11/main/postgresql.conf ```
Устанваливаем 
``` listen_addresses = '*' ```

В файле
``` /etc/postgresql/11/main/pg_hba.conf ```
Добавляем строчку 
``` host    all		all		172.0.0.0/8		md5 ```

каждый проект докера может использовать сети из этого диапазона. лучше открыть весь.

Перезапускаем postgresql
``` sudo systemctl restart postgresql ```

### 2. docker
смотри актульную информацию на https://docs.docker.com/engine/install/
```
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

Разрешить запускаться от простого пользователя
``` usermod -a -G docker $USER ```
потом убеждаемся что группа добавилась
``` groups ```
если нет. то прсото обновляем переменные окружения или перезаходим на сервер.

### 2.1 Docker-compose
```
sudo curl -L https://github.com/docker/compose/releases/download/1.25.3/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 3. git
```sudo apt-get install git ```

### 4. rsync
``` sudo apt-get install rsync ```

### 5. sshpass
``` sudo apt-get install sshpass ```

## Установить на контрольном хосте (машина с которой планируется разворачивание ПО)
### 1. ansible
``` sudo apt-get install ansible ```

## 2. sshpass
``` sudo apt-get install sshpass ```

## Перед разворачиванием
1. Устанавливаем на контрольный хост git
```sudo apt-get install git ```

2. Клонируем этот репозитарий на контрольный хост
``` git clone https://github.com/Alexander35/device_config_backup ```

3. переходим в папку проекта
``` cd device_config_backup ```

4. Находим в этом репозитарии в корневом катологе файл .inventory.yml и переименовываем .inventory.yml в inventory.yml. Исправляем значение ansible_host на айпи адрес сервера,  ansible_user - логин пользователя на сервере, ansible_password - пароль от сервера . Эти данные нужны для подключения по ssh.
```
ip_vlan_keeper_server:
  hosts:
      server1:
        ansible_connection: ssh
        ansible_host: "SERVER_IP"
        ansible_user: "SERVER_USER"
        ansible_password: "SERVER_USER_PASSWORD"
```

5. Переименовываем .playbook.yml в playbook.yml. В файле .playbook.yml.
Меняем значения переменных на нужные

папка для временных файлов проекта на сервере
```
clone_to: "/tmp/device_config_backup/"
```

папка временных фалов основного проекта и микросервисов
```
  device_config_backup_clone_to: "/tmp/device_config_backup/"
  rmq_postgres_commander_clone_to: "/tmp/rmq_postgres_commander/"
  rmq_telnet_operator_clone_to: "/tmp/rmq_telnet_operator/"
  rmq_ping_commander_clone_to: "/tmp/rmq_ping_commander/"
```

адрес сервера, используется на бэкенде для БД
название БД,
имя пользователя БД,
пароль пользователя БД,
логин администратора программы,
майл администратора программы,
пароль администратора программы,
```
  device_config_backup_host_address: "{{ansible_host}}"
  device_config_backup_db_name: "device_config_backup"
  device_config_backup_db_user_name: "device_config_backup"
  device_config_backup_db_password: "device_config_backup"
  device_config_backup_admin_name: "admin"
  device_config_backup_admin_email: "ad@m.in"
  device_config_backup_admin_password: "admin"
```

Эндпоинт для выгрузки информации по конфигурациям коммутаторов в Easy Crossing
```
  easy_crossing_post_address : ""
```

```
--- 
  - name: Deploy
    connection: ssh
    gather_facts: false
    hosts: all
    vars:
      device_config_backup_clone_to: "/tmp/device_config_backup/"
      device_config_backup_git_url: "https://github.com/Alexander35/device_config_backup.git"

      rmq_postgres_commander_clone_to: "/tmp/rmq_postgres_commander/"
      rmq_postgres_commander_git_url: "https://github.com/Alexander35/rmq_postgres_commander.git"

      rmq_telnet_operator_clone_to: "/tmp/rmq_telnet_operator/"
      rmq_telnet_operator_git_url: "https://github.com/Alexander35/rmq_telnet_operator.git"

      rmq_ping_commander_clone_to: "/tmp/rmq_ping_commander/"
      rmq_ping_commander_git_url: "https://github.com/Alexander35/rmq_ping_commander.git"

      device_config_backup_host_address: "{{ansible_host}}"
      device_config_backup_db_name: "device_config_backup"
      device_config_backup_db_user_name: "device_config_backup"
      device_config_backup_db_password: "device_config_backup"
      device_config_backup_admin_name: "admin"
      device_config_backup_admin_email: "ad@m.in"
      device_config_backup_admin_password: "admin"

      rmq_host: "amqp://guest:guest@172.17.0.1:5672"

      postgres_commander_rmq_exchange : "postgres_commander_rmq_exchange"
      postgres_commander_rmq_queue_in : "postgres_commander_rmq_queue_in"
      easy_crossing_post_address : ""

      rmq_telnet_operator_rmq_exchange: "rmq_telnet_operator_rmq_exchange"
      rmq_telnet_operator_rmq_queue_in: "rmq_telnet_operator_rmq_queue_in"
      rmq_telnet_operator_redirect_to_exchange: "{{postgres_commander_rmq_exchange}}"
      rmq_telnet_operator_redirect_to_queue: "{{postgres_commander_rmq_queue_in}}"

      rmq_ping_commander_rmq_exchange: "rmq_ping_commander_rmq_exchange"
      rmq_ping_commander_rmq_queue_in: "rmq_ping_commander_rmq_queue_in"

    tasks:
      - git:
          repo: "{{device_config_backup_git_url}}"
          dest: "{{device_config_backup_clone_to}}"
          update: yes

      - git:
          repo: "{{rmq_postgres_commander_git_url}}"
          dest: "{{rmq_postgres_commander_clone_to}}"
          update: yes

      - git:
          repo: "{{rmq_telnet_operator_git_url}}"
          dest: "{{rmq_telnet_operator_clone_to}}"
          update: yes

      - git:
          repo: "{{rmq_ping_commander_git_url}}"
          dest: "{{rmq_ping_commander_clone_to}}"
          update: yes

      - name: build images
        command: >
          docker-compose --log-level DEBUG --file {{device_config_backup_clone_to}}docker-compose.yml build
          --build-arg DEVICE_CONFIG_BACKUP_HOST_ADDRESS={{device_config_backup_host_address}}
          --build-arg DEVICE_CONFIG_BACKUP_DB_NAME={{device_config_backup_db_name}}
          --build-arg DEVICE_CONFIG_BACKUP_DB_USER_NAME={{device_config_backup_db_user_name}}
          --build-arg DEVICE_CONFIG_BACKUP_DB_PASSWORD={{device_config_backup_db_password}}
          --build-arg DEVICE_CONFIG_BACKUP_ADMIN_NAME={{device_config_backup_admin_name}}
          --build-arg DEVICE_CONFIG_BACKUP_ADMIN_EMAIL={{device_config_backup_admin_email}}
          --build-arg DEVICE_CONFIG_BACKUP_ADMIN_PASSWORD={{device_config_backup_admin_password}}
          --build-arg RMQ_HOST={{rmq_host}}
          --build-arg POSTGRES_COMMANDER_RMQ_EXCHANGE={{postgres_commander_rmq_exchange}}
          --build-arg POSTGRES_COMMANDER_RMQ_QUEUE_IN={{postgres_commander_rmq_queue_in}}
          --build-arg EASY_CROSSING_POST_ADDRESS={{easy_crossing_post_address}}
          --build-arg RMQ_TELNET_OPERATOR_RMQ_EXCHANGE={{rmq_telnet_operator_rmq_exchange}}
          --build-arg RMQ_TELNET_OPERATOR_RMQ_QUEUE_IN={{rmq_telnet_operator_rmq_queue_in}}
          --build-arg RMQ_TELNET_OPERATOR_REDIRECT_TO_EXCHANGE={{rmq_telnet_operator_redirect_to_exchange}}
          --build-arg RMQ_TELNET_OPERATOR_REDIRECT_TO_QUEUE={{rmq_telnet_operator_redirect_to_queue}}
          --build-arg RMQ_PING_COMMANDER_RMQ_EXCHANGE={{rmq_ping_commander_rmq_exchange}}
          --build-arg RMQ_PING_OPERATOR_RMQ_QUEUE_IN={{rmq_ping_commander_rmq_queue_in}} 

      - block:
        - name: stop container d_c_b
          command: docker stop d_c_b

        - name: rm container d_c_b
          command: docker rm d_c_b

        - name: stop container d_c_b_pgc
          command: docker stop d_c_b_pgc

        - name: rm container d_c_b_pgc
          command: docker rm d_c_b_pgc

        - name: stop container d_c_b_to
          command: docker stop d_c_b_to

        - name: rm container d_c_b_to
          command: docker rm d_c_b_to

        - name: stop container d_c_b_pc
          command: docker stop d_c_b_pc

        - name: rm container d_c_b_pc
          command: docker rm d_c_b_pc

        - name: rm container rmq
          command: docker rm rmq

        ignore_errors: yes

      - name: run images
        command: >
          docker-compose --file {{device_config_backup_clone_to}}docker-compose.yml up -d

```

## Разворачивание
1. Установить ansible на хосте, с которого предполагается деплой.
за подробной информацией https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

```
sudo add-apt-repository "deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main"
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
sudo apt update
sudo apt install ansible
```

При помощи ansible разворачиваем проект на сервере
``` ansible-playbook -i inventory.yml -vvvv playbook.yml ```
inventory.yml и playbook.yml - это файлы, описанные выше

## Бэкап БД
Записываем задания для бэкапа в cron на сервере
``` crontab -e ```

``` 23 23  */10  *  *  echo SERVER_USER_PASSWORD | sudo -S -u postgres pg_dump device_config_backup > /backup/folder/server/device_config_backup"$(date)".sql && sshpass -p "VAULT_USER_PASSWORD" rsync -avz --remove-source-files /backup/folder/server/ VAULT_USER@VAULT_IP:/backup/folder/vault ```

Чтобы удалить лишние файлы в хранилище рекомендуется в крон на хранилище добавить 
```  23 23  21  *  *   find /backup/folder/vault -type f -not -name '*20*' -delete ```
```  23 23  11  *  *   find /backup/folder/vault -type f -not -name '*10*' -delete ```

Все папки на хостах должны существовать и на них нужно установить соответствующие права доступа. И проверьте, что эти задачи работают без cron просто из консоли

чтобы исключить ошибку вида Host key verification failed. Нужно просто подключиться из консоли по ssh к нужному хосту.

## Восстановление БД
Чтобы восстановить БД из бэкапа. нужно закачать один файл с бэкапом с хранилища обратно на сервер
Затем заходим в postgres, удаляем базу и создаём снова пустую
``` sudo su postgres ```
``` psql ```
``` DROP DATABASE device_config_backup; ```
``` CREATE DATABASE device_config_backup; ```
``` GRANT ALL ON DATABASE device_config_backup TO device_config_backup; ```

Записываем в базу данные из бэкапа
``` echo SERVER_USER_PASSWORD | sudo -S -u postgres psql device_config_backup < "BACKUP_FILE.sql" ```


## Первоначальная задание паролей для доступа к устройствам
Это работает только если пароли для этой сети ещё не заданы
http://SERVERNAME:8809/assign_credentials_to_devices/192.168.0.0/16/LOGIN/PASSWORD

### Любые вопросы alexander.ivanov.35@gmail.com
