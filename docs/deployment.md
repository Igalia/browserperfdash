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
=> CRATE ROLE browserperf_user with password 'browserperf_pass';
=> GRANT ALL privileges ON DATABASE browserperfdash to browserperf_user; 
=> alter role browserperf_user with LOGIN;

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