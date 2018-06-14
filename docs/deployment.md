# Deploying `browserperfdash`

For how to deploy `browserperfdash` first check the [README.md](../README.md)

This document contains more specific instructions about how to setup the DB
with PostgreSQL for production

## Deploying `browserperfdash` with PostgreSQL

1. Install requirements
```
$ sudo apt-get install python3 python3-pip python3-dev virtualenvwrapper
$ sudo apt-get install postgresql python-psycopg2

```

2. Setup `PostgreSQL` database:

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

3. Update `browserperfdash/local_settings.py` with this data.
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

```
4. Update other settings in `browserperfdash/local_settings.py`:
```
SECRET_KEY = 'Your_Complicated_Key'
DEBUG = False
ALLOWED_HOSTS = [<enter_IP_address>, ]
```

5. Deploy on your webserver following:
https://docs.djangoproject.com/en/1.10/howto/deployment/
