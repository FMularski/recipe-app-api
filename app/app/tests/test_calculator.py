import pytest
from app import calc

@pytest.mark.parametrize('x, y, ex', [
    (1, 2, 3),
    (5, 7, 12),
    (0, 0, 0),
    (-5, 3, -2),
    (-3, -7, -10)
])
def test_calc_add(x, y, ex):
    res = calc.add(x, y)
    assert res == ex

@pytest.mark.parametrize('x, y, ex', [
    (4, 2, 2),
    (1, 4, -3),
    (0, 0, 0),
    (5, -3, 8),
    (-3, -4, 1),
])
def test_calc_sub(x, y, ex):
    res = calc.sub(x, y)
    assert res == ex