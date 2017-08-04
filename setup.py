#!/usr/bin/env python
from setuptools import setup

import datatrans

setup(
    name='django-datatrans-gateway',
    version=datatrans.__version__,
    description='',
    long_description='',
    author='Nicholas Wolff',
    author_email='nwolff@gmail.com',
    url=datatrans.__URL__,
    download_url='https://pypi.python.org/pypi/django-datatrans-gateway',
    packages=[
        'datatrans',
        'datatrans.migrations',
        'datatrans.views',
    ],
    package_data={'datatrans': [
        'templates/admin/datatrans/*.html',
        'templates/datatrans/example/*.html',
    ]},
    install_requires=[
        'Django>=1.7',
        'django-money',
        'requests',
        'defusedxml',
        'structlog',
        'typing',
    ],
    license=datatrans.__licence__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
