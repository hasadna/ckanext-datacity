#!/usr/bin/env bash

cd /opt/ckanext-datacity &&\
/opt/push_source_translations/venv/bin/pip install -e . &&\
/opt/push_source_translations/venv/bin/python setup.py extract_messages &&\
( cd /opt/push_source_translations/venv/src/ckan && /opt/push_source_translations/venv/bin/python setup.py extract_messages ) &&\
msgcat /opt/push_source_translations/venv/src/ckan/ckan/i18n/ckan.pot ckanext/datacity/i18n/ckanext-datacity.pot > ckanext/datacity/i18n/ckan-datacity.pot &&\
echo "[https://www.transifex.com]
api_hostname = https://api.transifex.com
hostname = https://www.transifex.com
password = $TRANSIFEX_API_TOKEN
username = api
" > ~/.transifexrc &&\
tx push -s
