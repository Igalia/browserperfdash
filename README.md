# Igalia Browsers Performance Dashboard

[![Build Status](https://travis-ci.org/Igalia/browserperfdash.svg?branch=master)](https://travis-ci.org/Igalia/browserperfdash)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

The applicaiton powers https://browserperfdash.igalia.com and provides a dashboard to analyze browser perofrmance reports. Bots 
send in the data via `POST` APIs and the application perfroms the number crunching. 

## Collect Pre-requisites
Install `python-pip`, `python-dev` and `virtualenvwrapper`
```bash
sudo apt-get install python-pip python-dev memcached
sudo pip install virtualenvwrapper
```

## Get the files
You can clone it directly from [https://github.com/Igalia/browserperfdash](https://github.com/Igalia/browserperfdash)
```bash
git clone https://github.com/Igalia/browserperfdash
```

## Setup development environment
First, some initialization steps. Most of this only needs to be done
one time. You will want to add the command to source
`/usr/local/bin/virtualenvwrapper.sh` to your shell startup file
(`.bashrc` or `.zshrc`) changing the path to `virtualenvwrapper.sh`
depending on where it was installed by `pip`.
```bash
export WORKON_HOME=~/Envs
mkdir -p $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
```

Lets create a virtual environment for our project
```bash
mkvirtualenv dashboard
workon dashboard
```

## Install requirements
All the requirements are mentioned in the file `requirements.txt`.
```bash
pip install -r requirements.txt
```

## Setup database
Setup tables in the DB
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
Collect all the static files for fast serving
```bash
python manage.py collectstatic
```

Create `browserperfdash/local_settings.py` with local configurations
```bash
mv docs/local-settings.py browserperfdash/local_settings.py
```


## Run server
```bash
python manage.py runserver
```
