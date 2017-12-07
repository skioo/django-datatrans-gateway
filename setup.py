#!/usr/bin/env python
from setuptools import setup

import datatrans

setup(
    name='django-datatrans-gateway',
    version=datatrans.__version__,
    description='Integrate django with the datatrans payment service provider',
    long_description='',
    author='Nicholas Wolff',
    author_email='nwolff@gmail.com',
    url=datatrans.__URL__,
    download_url='https://pypi.python.org/pypi/django-datatrans-gateway',
    packages=[
        'datatrans',
        'datatrans.gateway',
        'datatrans.views',
        'datatrans.migrations',
    ],
    package_data={'datatrans': [
        'templates/admin/datatrans/*.html',
        'templates/datatrans/example/*.html',
    ]},
    install_requires=[
        'Django>=1.8',
        'django-money',
        'requests',
        'defusedxml',
        'structlog',
        'typing',
    ],
    license=datatrans.__licence__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
