"""
WSGI config for CareerAdvisor project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareerAdvisor.settings')

application = get_wsgi_application()
