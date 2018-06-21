# Deploying `browserperfdash` for production

This document contains more specific instructions about how to setup the DB
with PostgreSQL for production

## Install dependendencies and fetch the code

1. Install dependendencies

```bash
$ sudo apt-get install python3 python3-pip python3-dev virtualenvwrapper
$ sudo apt-get install postgresql python-psycopg2

```

2. Get the files
You can clone it directly from [https://github.com/Igalia/browserperfdash](https://github.com/Igalia/browserperfdash)
```bash
mkdir /srv
cd /srv
git clone https://github.com/Igalia/browserperfdash
```

## Setup the python virtual environment and install pip requirements

1. Setup python virtual environment

```bash
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
export WORKON_HOME=/srv/browserperfdash/venv
mkdir ${WORKON_HOME}
```


2. Create a virtual environment `dashboard` for our project

```bash
mkvirtualenv -p /usr/bin/python3 dashboard
workon dashboard
```

3. Install pip requirements on the virtual environment

```
cd /srv/browserperfdash
pip install -r requirements.txt
```

## Setup the database with PostgreSQL and the app config

1. Create a new DB.

```
$ sudo -i
$ su - postgres
$ createdb browserperfdash
$ psql
=> CREATE ROLE browserperf_user with password 'browserperf_pass';
=> GRANT ALL privileges ON DATABASE browserperfdash to browserperf_user;
=> alter role browserperf_user with LOGIN;
=> \q
$ exit
$ exit
```

2. Copy default local_settings.py

```bash
cp docs/local-settings.py browserperfdash/local_settings.py
```

3. Update the DATABASE type in `browserperfdash/local_settings.py` with this data.

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'browserperfdash',
        'USER': 'browserperf_user',
        'PASSWORD': 'browserperf_pass',
        'HOST': 'localhost',
        'PORT': '',
    }
}


4. Update other settings in `browserperfdash/local_settings.py`:
```
SECRET_KEY = 'Your_Complicated_Key'
DEBUG = False
ALLOWED_HOSTS = [<enter_IP_address>, ]
```

5. Setup initial tables in the DB
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. Collect all the static files for fast serving
```bash
python manage.py collectstatic
```

## Deploy HTTP server and running the app

Since the app runs on a python virtual environment we have stored inside
the subfolder venv of the rootdir, each time we want to run the app or
nanage it via ```python manage.py``` we have to enter the virtual env via:

```bash
cd /srv/browserperfdash
source venv/dashboard/bin/activate
```

To run the app via an apache webserver we can use the provided [wsgy.py](../browserperfdash/wsgi.py] module.

First ensure Apache and the wsgi module is installed

```bash
$ sudo apt-get install apache2 libapache2-mod-wsgi-py3


Then configure a virtual site, this is an example of how it can be done:

```
<VirtualHost>

    ServerAdmin admin@igalia.com
    Alias /favicon.ico /srv/browserperfdash/static/favicon.ico
    Alias /static/ /srv/browserperfdash/static/
    <Directory /srv/browserperfdash/static>
        Require all granted
    </Directory>

    WSGIDaemonProcess browserperfdash python-home=/srv/browserperfdash/venv/dashboard python-path=/srv/browserperfdash

    WSGIProcessGroup browserperfdash
    WSGIApplicationGroup %{GLOBAL}

    WSGIScriptAlias / /srv/browserperfdash/browserperfdash/wsgi.py
    AllowEncodedSlashes NoDecode

    <Directory /srv/browserperfdash/browserperfdash>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/browserperfdash-error.log
    CustomLog ${APACHE_LOG_DIR}/browserperfdash-access.log combined

</VirtualHost>
```

If you need more info or you want to use other webserver like Nginx, please
check the Django deployment guide:
https://docs.djangoproject.com/en/1.10/howto/deployment/


### Set the allowed hosts list

Edit browserperfdash/local_settings.py and set the list of IPs and/or hostnames
where the service will be hosted (this should match the hostname set by the
webserver)

Example:
```
# [...]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["browserperfdash.igalia.com", "browserperfdash.intranet.igalia.com", "localhost", "127.0.0.1", "10.10.1.137"]
CSRF_COOKIE_DOMAIN = '.igalia.com'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
# [...]
```

## Initial configuration of the benchmarks and metric units

You can import this partial dump that will fill the metric units and benchmark
plans.

```bash
$ su - postgres
$ cat docs/initial_data_postgresql.dump | psql browserperfdash
COPY 8
COPY 13
```

After that you only need to fill the GPU/CPU/platform/bot/browser entries
and start deploying bots to send data.
For that you can use the script `browserperfdash-benchmark` that you can
find on the WebKit repository (or, alternatively at https://github.com/Igalia/browserperfrunner)
