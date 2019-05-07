from typing import Any

EXCLUDED = ['id', '_state']


def assertModelEqual(o1: Any, o2: Any):
    """
    asserting o1 == o2 yields confusing error messages, where it is impossible to
    know exactly which attribute is not-equal. Instead we iterate on attributes and compare
    one-by-one.
    """
    for k in vars(o1).keys():
        if k not in EXCLUDED:
            v1 = getattr(o1, k)
            v2 = getattr(o2, k)
            assert v1 == v2, "o['{}']: {} != {}".format(k, v1, v2)
