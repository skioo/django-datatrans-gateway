#!/usr/bin/env python
import sys

import django
import os
import warnings

if __name__ == '__main__':
    tests = sys.argv[1:] or ['tests']
    warnings.simplefilter('always', DeprecationWarning)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

    if hasattr(django, 'setup'):
        django.setup()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from django.test.runner import DiscoverRunner as TestRunner
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner as TestRunner

    test_runner = TestRunner()
    failures = test_runner.run_tests(tests)
    sys.exit(bool(failures))
