# ckanext-datacity

## Install

Standard CKAN plugin installation

```
plugins = ... datacity
```

Includes ckanext-scheming schemas, to use, add the following to config:

```
plugins = ... scheming_datasets scheming_groups

scheming.dataset_schemas = ckanext.datacity:scheming-dataset.json ckanext.datacity:scheming-app.json
scheming.group_schemas = ckanext.datacity:scheming-group-settings.json ckanext.datacity:scheming-group-automation.json

datacity.settings_group_id = settings
```

## Local plugin development

Prerequisites

* Verify Python version, it should be Python 3.10: `python --version`
* Install Docker & Docker Compose
* Clone of hasadna/ckan-cloud-docker at ../ckan-cloud-docker

Initialize

```
python 3.10 -m venv venv3
. venv3/bin/activate
pip install --upgrade pip
pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.11.2#egg=ckan[requirements]'
docker compose up -d redis solr db
docker compose exec -u postgres db createuser -S -D -R -P ckan_default
docker compose exec -u postgres db createdb -O ckan_default ckan_default -E utf-8
mkdir venv3/etc
ckan generate config venv3/etc/development.ini
mkdir venv3/storage
```

Edit the created config file (`venv/etc/development.ini`) and set the following:

```
sqlalchemy.url = postgresql://ckan_default:pass@127.0.0.1/ckan_default
ckan.storage_path = /absolute/path/to/venv/storage 
```

Install the requirements:

```
pip install -r requirements.txt
```

Install the datacity plugin

```
pip install -e .
```

Create the DB tables:

```
( cd venv3/src/ckan && ckan -c ../../etc/development.ini db init ) 
```

Edit the configuration (`venv3/etc/development.ini`):

```
ckan.plugins = activity datacity scheming_datasets scheming_groups pages

scheming.dataset_schemas = ckanext.datacity:scheming-dataset.json
scheming.group_schemas = ckanext.datacity:scheming-group-settings.json ckanext.datacity:scheming-group-automation.json
```

Create admin user

```
ckan -c venv3/etc/development.ini user add admin email=admin@localhost password=12345678
ckan -c venv3/etc/development.ini sysadmin add admin
```

(optional) to enable debugging - install dev requirements - `pip install -r venv/src/ckan/dev-requirements.txt` and set debug=true in `venv/etc/development.ini`

(optional) copy relevant ckan configs from an existing datacity instance in hasadna/datacity-k8s/instances/INSTANCE_NAME/values.yaml to `venv/etc/development.ini`

#### Start the development server

```
docker compose up -d redis solr db
. venv3/bin/activate
( cd venv3/src/ckan && ckan -c ../../etc/development.ini run )
```

Stop all containers

```
docker-compose down
```

#### Get latest translations from Transifex

Get the Transifex API token

```
export TX_TOKEN=
```
* Install [Transifex Client](https://developers.transifex.com/docs/cli#installation)
* Install gettext: `sudo apt-get install gettext`

Get the translations and copy to the local CKAN source

```
mkdir -p venv3/src/ckan/ckan/i18n/en_US/LC_MESSAGES/
mv venv3/src/ckan/ckan/i18n/en_GB/LC_MESSAGES/ckan.mo venv3/src/ckan/ckan/i18n/en_US/LC_MESSAGES/ckan.mo
for LANG in he ar en_US; do
    echo downloading $LANG &&\
    tx pull -tl $LANG &&
    mv ckanext/datacity/i18n/$LANG/LC_MESSAGES/ckan-datacity.po venv3/src/ckan/ckan/i18n/$LANG/LC_MESSAGES/ckan.po &&\
    echo compiling $LANG &&\
    msgfmt -o venv3/src/ckan/ckan/i18n/$LANG/LC_MESSAGES/ckan.mo venv3/src/ckan/ckan/i18n/$LANG/LC_MESSAGES/ckan.po &&\
    echo OK
done
```

### Updating source translation strings

This should be done when changes are made to either the source CKAN version or to the datacity extension

Activate the local development server with the relevant CKAN version (following the instructions above for local plugin development)

```
. venv/bin/activate
```

Install translation requirements

```
pip install --upgrade Babel
```

Update the .pot files

```
python setup.py extract_messages &&\
( cd venv/src/ckan && python setup.py extract_messages )
```

Merge the .pot files

```
msgcat venv/src/ckan/ckan/i18n/ckan.pot ckanext/datacity/i18n/ckanext-datacity.pot > ckanext/datacity/i18n/ckan-datacity.pot
```

Install Transifex CLI client - https://developers.transifex.com/docs/cli

Get a Transifex API token

```
TRANSIFEX_API_TOKEN=
```

Set transifex auth file

```
echo "[https://www.transifex.com]
api_hostname  = https://api.transifex.com
hostname      = https://www.transifex.com
username      = api
password      = ${TRANSIFEX_API_TOKEN}
rest_hostname = https://rest.api.transifex.com
token         = ${TRANSIFEX_API_TOKEN}
" > ~/.transifexrc
```

Push the updated .pot file

```
tx push -s
```

## Enabling datastore and xloader for local development

### Install

```
docker-compose exec -u postgres db createuser -S -D -R -P -l datastore_default
docker-compose exec -u postgres db createdb -O ckan_default datastore_default -E utf-8
```

Edit `venv/etc/development.init`:

* Add to ckan.plugins: `datastore xloader`
* `ckan.datastore.write_url = postgresql://ckan_default:123456@127.0.0.1/datastore_default`
* `ckan.datastore.read_url = postgresql://datastore_default:123456@127.0.0.1/datastore_default`
* `ckanext.xloader.unicode_headers = True`

set datastore permissions

```
paster --plugin=ckan datastore -c venv/etc/development.ini set-permissions | docker-compose exec -T -u postgres db psql
```

### Usage

Start CKAN normally

Start the Jobs service

```
. venv/bin/.activate
paster --plugin=ckan jobs -c venv/etc/development.ini worker
```

## Initializing the instance with data and settings

```
# Get the api key from the admin user page on the ckan instance
export CKAN_INSTANCE_DEV_API_KEY=
IMAGE="$(curl -s https://raw.githubusercontent.com/hasadna/hasadna-k8s/refs/heads/master/apps/datacity/values-hasadna-auto-updated.yaml | grep ckanDgpServerImage | cut -d' ' -f2)"
IMAGE="$(echo $IMAGE | sed 's/docker.pkg.github.com/ghcr.io/')"
docker run --network host -it --entrypoint python \
    -e CKAN_INSTANCE_DEV_URL=http://localhost:5000 -e CKAN_INSTANCE_DEV_API_KEY \
    $IMAGE -m datacity_ckan_dgp.operators.instance_initializer '{
        "instance_name": "dev",
        "default_organization_title": "עיריית חיפה",
        "muni_filter_texts": "חיפה,חייפה"
    }'
```

