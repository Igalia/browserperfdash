# Setting up the PostgresSQL database with the `browserperfdash`

1. Install Debian package dependendencies

```bash
$ sudo apt-get install postgresql
```

2. Create a new DB.

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

3. Copy default local_settings.py

```bash
cp docs/local-settings.py browserperfdash/local_settings.py
```

4. Update the DATABASE type in `browserperfdash/local_settings.py` with this data.

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


5. Update other settings in `browserperfdash/local_settings.py`:
```
SECRET_KEY = 'Your_Complicated_Key'
DEBUG = False
ALLOWED_HOSTS = [<enter_IP_address>, ]
```

6. Setup initial tables in the DB
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

7. Collect all the static files for fast serving
```bash
python manage.py collectstatic
```