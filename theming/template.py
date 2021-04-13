# -*- coding:utf-8 -*-
"""
@author: wTayyeb  https://github.com/wtayyeb
@license: MIT
"""

import io

from django.conf import settings
from django.template import TemplateDoesNotExist, Origin
from django.templatetags.static import static
from django.utils._os import safe_join

from .models import thememanager
from .threadlocals import get_thread_variable

from django.core.exceptions import SuspiciousFileOperation
from django.template.loaders.filesystem import Loader as BaseLoader


class Loader(BaseLoader):
    is_usable = True


    def get_contents(self, origin):
        try:
            with open(origin.template_name, encoding=self.engine.file_charset) as fp:
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
                yield Origin(
                    name=template_name,
                    template_name=safe_join(template_dir, template_name),
                    loader=self,
                )

            except SuspiciousFileOperation:
                # The joined path was located outside of this template_dir
                # (it might be inside another one, so this isn't fatal).
                pass

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
    return {
        'theme_url': theme_url,
        'sitetheme': theme,
        'site_title': sitetheme.site_title,
        'site_description': sitetheme.site_description,
    }
