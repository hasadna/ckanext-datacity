# ckanext-datacity

## Install

Standard CKAN plugin installation

```
plugins = ... datacity
```

Includes ckanext-scheming schemas, to use, add the following to config:

```
plugins = ... scheming_datasets

scheming.dataset_schemas = ckanext.datacity:scheming-dataset.json
```

## Local plugin development

Prerequisites

* Verify Python version, it should be Python 2.7: `python --version`
* Install Python virtualenv: `sudo apt-get install python-virtualenv`
* Install Docker & Docker Compose
* Clone of hasadna/ckan-cloud-docker at ../ckan-cloud-docker

Initialize

```
virtualenv --python python2 venv
. venv/bin/activate
pip install setuptools==36.1
pip install -e 'git+https://github.com/hasadna/ckan.git@master#egg=ckan'
pip install -r venv/src/ckan/requirements.txt
docker-compose up -d
docker-compose exec -u postgres db createuser -S -D -R -P ckan_default
docker-compose exec -u postgres db createdb -O ckan_default ckan_default -E utf-8
mkdir venv/etc
paster make-config ckan venv/etc/development.ini
ln -s `pwd`/venv/src/ckan/who.ini `pwd`/venv/etc/who.ini
mkdir venv/storage
```

Edit the created config file (`venv/etc/development.ini`) and set the following:

```
sqlalchemy.url = postgresql://ckan_default:pass@127.0.0.1/ckan_default
solr_url = http://127.0.0.1:8983/solr/ckan
ckan.site_url = http://localhost:5000
ckan.storage_path = /absolute/path/to/venv/storage
```

Create the DB tables:

```
( cd venv/src/ckan && paster db init -c `pwd`/../../etc/development.ini )
```

Install the datacity CKAN requirements:

```
pip install -r ../ckan-cloud-docker/ckan/requirements.txt
```

Install the datacity plugin

```
pip install -e .
```

Edit the configuration (`venv/etc/development.ini`):

add `datacity` to ckan.plugins

Create admin user

```
( cd venv/src/ckan && paster sysadmin add admin -c `pwd`/../../etc/development.ini )
```

(optional) to enable debugging - install dev requirements - `pip install -r venv/src/ckan/dev-requirements.txt` and set debug=true in `venv/etc/development.ini`

(optional) copy relevant ckan configs from an existing datacity instance in hasadna/datacity-k8s/instances/INSTANCE_NAME/values.yaml to `venv/etc/development.ini`

#### Start the development server

```
docker-compose up -d
. venv/bin/activate
( cd venv/src/ckan && paster serve `pwd`/../../etc/development.ini )
```

Stop all containers

```
docker-compose down
```

#### Get latest translations from Transifex

Get the Transifex API token

```
TRANSIFEX_API_TOKEN=
```

Get the translations and copy to the local CKAN source

```
for LANG in he ar en_US; do
    echo downloading $LANG &&\
    curl -sL --user api:$TRANSIFEX_API_TOKEN -X GET "https://www.transifex.com/api/2/project/datacity-ckan/resource/ckanpot/translation/$LANG/?mode=default&file" > venv/src/ckan/ckan/i18n/$LANG/LC_MESSAGES/ckan.po &&\
    echo compiling $LANG &&\
    msgfmt -o venv/src/ckan/ckan/i18n/$LANG/LC_MESSAGES/ckan.mo venv/src/ckan/ckan/i18n/$LANG/LC_MESSAGES/ckan.po &&\
    echo OK
done
```
