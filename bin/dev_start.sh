#!/usr/bin/env bash
shopt -s globstar
files=(ckanext/datacity/templates/**/*.html)
args=()
for file in "${files[@]}"; do
    args+=("-e" "$(pwd)/$file")
done
files=(venv3/src/ckan/ckan/templates/**/*.html)
for file in "${files[@]}"; do
    args+=("-e" "$(pwd)/$file")
done

cd venv3/src/ckan
ckan -c ../../etc/development.ini run "${args[@]}"
