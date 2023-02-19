FROM ubuntu:18.04
RUN mkdir /opt/push_source_translations &&\
    cd /opt/push_source_translations &&\
    apt-get update && apt-get install -y python-virtualenv git gettext &&\
    virtualenv -p python2 venv &&\
    venv/bin/pip install setuptools==36.1 &&\
    venv/bin/pip install -e 'git+https://github.com/hasadna/ckan.git@master#egg=ckan' &&\
    venv/bin/pip install -r venv/src/ckan/requirements.txt &&\
    venv/bin/pip install --upgrade Babel
RUN curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT /entrypoint.sh
