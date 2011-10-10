#!/bin/bash

#JANGY_ROOT=/Users/fish/Dropbox/local-instance-packages/Django-1.4-alpha-16933
#export JANGY_ROOT

echo "Running django-sonnar tests..."
${JANGY_ROOT}/django/bin/django-admin.py test core \
--settings=settings \
--verbosity=2 \
--nocapture --nologcapture
