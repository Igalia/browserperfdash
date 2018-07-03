# Igalia Browsers Performance Dashboard

[![Build Status](https://travis-ci.org/Igalia/browserperfdash.svg?branch=master)](https://travis-ci.org/Igalia/browserperfdash)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

The application powers https://browserperfdash.igalia.com and provides a dashboard to analyze browser perofrmance reports.

Bots send in the data via `POST` APIs and the application perfroms the number crunching.


# Deploying `browserperfdash`

For how to deploy `browserperfdash` check the following documents:

* For development or testing productions (SQLite DB + built-in http server): [docs/deployment-development.md](docs/deployment-development.md)
* For production deployments (PostgreSQL DB + Apache or Nginx fronted): [docs/deployment-production.md](docs/deployment-production.md)


# Running benchmarks and sending data to `browserperfdash`

For that you can use the script `browserperfdash-benchmark` that you can
find on the WebKit repository (or, alternatively at https://github.com/Igalia/browserperfrunner)

