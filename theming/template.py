# -*- coding:utf-8 -*-
"""
@author: wTayyeb  https://github.com/wtayyeb
@license: MIT
"""

import io

from django.conf import settings
from django.template import Origin
from django.template import TemplateDoesNotExist
from django.templatetags.static import static
from django.utils._os import safe_join

from .models import thememanager, SiteTheme

try:
    from django_common.theadlocal import get_thread_variable
except ImportError:
    from .threadlocals import get_thread_variable

try:
    from django.core.exceptions import SuspiciousFileOperation
except ImportError:
    from django.core.exceptions import SuspiciousOperation as SuspiciousFileOperation

try:
    from django.template.loaders.base import Loader as BaseLoader
except ImportError:
    from django.template.loader import BaseLoader


class Loader(BaseLoader):
    is_usable = True

    def get_contents(self, origin):
        try:
            with open(origin.name, encoding=self.engine.file_charset) as fp:
                return fp.read()
        except FileNotFoundError:
            raise TemplateDoesNotExist(origin)

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        theme = thememanager.get_current_theme()

        if not template_dirs:
            from .models import Theme
            template_dirs = [safe_join(Theme.get_theming_root(theme.slug), theme.slug), ]


        for template_dir in template_dirs:
            try:
                name = safe_join(template_dir, template_name)
            except SuspiciousFileOperation:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                continue

            yield Origin(
                name=name,
                template_name=template_name,
                loader=self,
            )

    def load_template_source(self, template_name, template_dirs=None):
        tried = []
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                with io.open(filepath, encoding=self.engine.file_charset) as fp:
                    return fp.read(), filepath
            except IOError:
                tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = ("Your template directories configuration is empty. "
                         "Change it to point to at least one template directory.")
        raise TemplateDoesNotExist(error_msg)

    load_template_source.is_usable = True


def context_processor(request):
    """ theming template context processor """
    theme = thememanager.get_current_theme()
    theme_url = settings.THEMING_URL
    theme_url += '/' if theme_url[-1] != '/' else ''
    theme_url = static(theme_url + theme.slug).replace('\\', '/')
    sitetheme = get_thread_variable('sitetheme')
    if not sitetheme:
        sitetheme = SiteTheme.objects.get(
            theme_slug=settings.THEMING_DEFAULT_THEME
        )
    return {
        'theme_url': theme_url,
        'sitetheme': theme,
        'site_title': sitetheme.site_title,
        'site_description': sitetheme.site_description,
    }
