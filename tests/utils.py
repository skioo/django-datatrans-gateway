from typing import Any, Sequence


def _dict_without_excluded(o: Any, excluded_keys: Sequence[str] = ['_state']):
    return {k: v for k, v in vars(o).items() if k not in excluded_keys}


def assertModelEqual(o1: Any, o2: Any):
    assert _dict_without_excluded(o1) == _dict_without_excluded(o2)
