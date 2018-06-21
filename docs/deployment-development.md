# Deploying `browserperfdash` for development or testing

This document contains instructions about how to quickly start running
browserperfdash for development or testing with SQLite and the built-in
HTTP server.

For production deployments, instead is recommended deploying with PostgreSQL
and with an Apache or Nginx fronted. For that following the guide [deployment-production.md](deployment-production.md) instead.

## Install dependendencies and fetch the code

1. Install Debian package dependendencies

```bash
$ sudo apt-get install python3 python3-pip python3-dev virtualenvwrapper

```

2. Get the files

You can clone it directly from [https://github.com/Igalia/browserperfdash](https://github.com/Igalia/browserperfdash)

```bash
git clone https://github.com/Igalia/browserperfdash
```

## Setup the python virtual environment and install pip requirements

1. First, source the python virtual env tooling

```bash
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
```

Notes:

 * if installed via pip, the wrapper is usually at /usr/local/bin/virtualenvwrapper.sh
 * if you usually work with python virtual envs, it may be a good idea
   to add the above source command to your shell startup file (`.bashrc` or `.zshrc`)
   to have it automatically ready


2. Lets create a virtual environment `dashboard` for our project
```bash
mkvirtualenv -p /usr/bin/python3 dashboard
workon dashboard
```

3. Install pip requirements on the virtual environment

All the requirements are mentioned in the file `requirements.txt`.
```bash
cd /path/to/git/checkout/browserperfdash
pip install -r requirements.txt
```

## Setup the database with SQLite


1. Copy default local_settings.py

```bash
cp docs/local-settings.py browserperfdash/local_settings.py
```

2. Setup tables in the DB

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

3. Collect all the static files for fast serving

```bash
python manage.py collectstatic
```

## Run built-in HTTP server

```bash
python manage.py runserver
```
