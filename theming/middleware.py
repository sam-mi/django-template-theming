# -*- coding:utf-8 -*-
'''
@author: wTayyeb  https://github.com/wtayyeb
@license: MIT
'''
import logging
from django.contrib.sites.models import Site, SITE_CACHE
from django.conf import settings

from theming.models import SiteTheme

try:
    from django_common.theadlocal import set_thread_variable
except ImportError:
    from .threadlocals import set_thread_variable

logger = logging.getLogger(__name__)

class ThemingMiddleware(object):
    ''' Middleware that puts the request object in thread local storage.

        add this middleware to MIDDLEWARE_CLASSES to make theming work.

        MIDDLEWARE_CLASSES	 = (
            ...
            'theming.middleware.ThemingMiddleware',
        )

    '''
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    def process_request(self, request):
        try:
            host = request.get_host()
            if host not in SITE_CACHE:
                site = Site.objects.get(domain__iexact=host)
                SITE_CACHE[host] = site
            site = SITE_CACHE[host]
        except (Site.DoesNotExist, KeyError):
            logger.warning(
                f"Site object not found by domain__iexact=host with host {host}"
            )
            site = Site.objects.filter(pk=settings.SITE_ID)
            site = site[0] if site else None

        try:
            sitetheme = site.sitetheme
        except (AttributeError):
            sitetheme = SiteTheme.objects.first()

        set_thread_variable(settings.THEMING_APP_NAME, sitetheme)
