Django Template Theming
***********************

.. image:: https://travis-ci.org/wtayyeb/django-template-theming.svg?branch=master
    :target: https://travis-ci.org/wtayyeb/django-template-theming

Django application, implement theming concept for templates, flexible and configurable from admin interface.

Installation
============

You can install the most recent **Django Template Theming** version using pip: ::

    pip install django-template-theming

Setup
=====

**NOTE**: The following settings should be added to the project file `settings.py`.

1. Add 'theming' to ``INSTALLED_APPS``: ::

    INSTALLED_APPS += ( 'theming', )
    
    if using django-compressor make sure put theming before compressor

2. Add 'theming.middleware.ThemingMiddleware' to ``MIDDLEWARE_CLASSES``: ::

    MIDDLEWARE_CLASSES += ( 'theming.middleware.ThemingMiddleware', )

3. Add 'theming.template.Loader' to ``TEMPLATE_LOADERS``: ::

    TEMPLATE_LOADERS += ( 'theming.template.Loader', )

Usage
=====

It should create a folder ``themes`` at the project with the following structure: ::

    django_project/
    | -- themes/
        | -- default/  ** theme name
            | -- static/  ** will collected by `collectstatic` management command
            |   | -- styles/
            |   | -- scripts/
            |   | -- images/
            | -- templatefiles and folders


Installable Themes

To install a theme add it to ``INSTALLED_APPS``, then define ``THEMING_APPS`` dict with the theme slug as
the key and the app label as the value e.g. ::

    THEMING_ROOT = 'themes'
    THEMING_APPS = {
        'default': 'my_default_theme_app', # could be the project app or an installed theme.
        'mytheme': 'my_theme',
        'slug': 'app_label', # example format
    }




Contributing
============

Development of **django-template-theming** happens at github and any idea and contribution is welcome.
https://github.com/wtayyeb/django-template-theming

Credits
=======

* w.Tayyeb: https://github.com/wtayyeb
