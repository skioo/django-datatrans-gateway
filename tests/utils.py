from typing import Any, Sequence
from unittest import TestCase


def _dict_without_excluded(o: Any, excluded_keys: Sequence[str] = ['_state']):
    return {k: v for k, v in vars(o).items() if k not in excluded_keys}


def assertModelEqual(testCase: TestCase, o1: Any, o2: Any):
    testCase.assertEqual(_dict_without_excluded(o1), _dict_without_excluded(o2))
