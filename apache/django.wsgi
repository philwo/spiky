import os, sys
sys.path.append('/home/philwo/www/spiky.phorge.de/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'spiky.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

