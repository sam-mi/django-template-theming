# -*- coding:utf-8 -*-
"""
@author: wTayyeb  https://github.com/wtayyeb
@license: MIT
"""

import json
import logging
import os

from django.conf import settings
from django.contrib.sites.models import Site, SITE_CACHE
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .threadlocals import get_thread_variable

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Theme(object):
    _metadata_filename = 'metadata.json'

    def __init__(self, slug, *args, **kwargs):
        super(Theme, self).__init__(*args, **kwargs)

        self.slug = slug
        self._metadata = {}
        self.metadata_ready = None

    def get_theming_root(self, theme_slug=None):
        root = settings.THEMING_ROOT if hasattr(settings, 'THEMING_ROOT') else 'themes'
        if theme_slug:
            theme_app = settings.THEMING_APPS[theme_slug]
            theme_app = __import__(theme_app)
            root = os.path.join(theme_app.__file__).replace(
                '__init__.py', settings.THEMING_ROOT
            )
        else:
            if hasattr(settings, 'THEMING_APPS') and settings.THEMING_APPS is not None:
                root_list = []
                for theme, app in settings.THEMING_APPS.items():
                    theme_app = __import__(app)

                    # Get the THEMING_ROOT for a loaded theme app.
                    # Theme apps should use the same construction i.e.
                    # the THEMING_ROOT and folder layout should be standardised.
                    root = os.path.join(theme_app.__file__).replace(
                        '__init__.py', settings.THEMING_ROOT
                    )
                    root_list.append(root)
                return root_list
            return [root]
        # used by read_metadata or by passing a theme_slug to return a
        # a single root rather than a list.
        return root

    def read_metadata(self):
        # filename = os.path.join(settings.THEMING_ROOT, self.slug, self._metadata_filename)
        filename = os.path.join(
            self.get_theming_root(thememanager.get_current_theme().slug),
            self.slug, self._metadata_filename
        )
        try:
            with open(filename, 'r') as f:
                self._metadata = json.load(f)
                self.metadata_ready = True
        except IOError:
            self._metadata = {}
            self.metadata_ready = False

    def __getattr__(self, key):
        if key not in ('name', 'description', 'author', 'version'):
            raise AttributeError

        if self.metadata_ready is None:
            self.read_metadata()

        if self.metadata_ready is False:
            logger.debug('theme %s have no metadata or its metadata is not a valid json' % self.slug)

        val = self._metadata.get(key)

        if val is None and key is 'name':
            val = self.slug.title()

        return val

    def __str__(self, *args, **kwargs):
        return '<Theme `%s`>' % self.slug


class ThemeManager(object):
    def __init__(self, *args, **kwargs):
        super(ThemeManager, self).__init__(*args, **kwargs)

        self._themes = None
        self.host = None

    def find_themes(self, force=False):
        if self._themes is None or force:
            self._themes = {}
            root_list = Theme.get_theming_root(settings.THEMING_ROOT) # Theme.get_theming_root
            # make root a list
            for root in root_list:
                for dirname in os.listdir(root):
                    if not dirname.startswith('~'):
                        self._themes[dirname] = Theme(dirname)
        return self._themes

    def get_themes_choice(self):
        themes = self.find_themes()
        choices = []
        for theme in themes.values():
            choices.append((theme.slug, theme.name))
        return choices

    def get_current_theme(self):
        sitetheme = get_thread_variable('sitetheme')
        if sitetheme:
            theme = sitetheme.theme
        else:
            if not hasattr(settings, 'THEMING_DEFAULT_THEME'):
                theme = self.get_theme('default')
            else:
                theme = self.get_theme(settings.THEMING_DEFAULT_THEME)
        return theme

    def get_theme(self, theme_slug='default'):
        self.find_themes()
        return self._themes[theme_slug]


thememanager = ThemeManager()


@python_2_unicode_compatible
class SiteTheme(models.Model):
    site = models.OneToOneField(Site)
    theme_slug = models.CharField(max_length=100, choices=thememanager.get_themes_choice())
    site_title = models.CharField(max_length=255, default='', blank=True)
    site_description = models.CharField(max_length=255, default='', blank=True)

    @property
    def theme(self):
        return thememanager.get_theme(self.theme_slug)

    def __str__(self):
        theme = self.theme
        return '%s : [%s] %s' % (self.site, theme.slug, theme.name)

    def delete(self, using=None):
        SITE_CACHE.pop(self.site.domain, None)
        return super(SiteTheme, self).delete(using=using)

    def save(self, *args, **kwargs):
        SITE_CACHE.pop(self.site.domain, None)
        return super(SiteTheme, self).save(*args, **kwargs)
