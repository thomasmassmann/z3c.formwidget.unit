# -*- coding: utf-8 -*-
"""Unit conversion utilities."""

# local imports
from z3c.formwidget.unit import interfaces


def get_best_unit(value, system, dimension, level_min=0, level_max=None):
    """Return the unit that fits best."""
    level = 0
    if dimension == interfaces.DIMENSION_AREA:
        level = 2
        if value < 1000:
            level = 0
        elif value <= 1000000:
            level = 1
    elif dimension == interfaces.DIMENSION_LENGTH:
        level = 2
        if value < 0.5:
            level = 0
        elif value > 400:
            level = 3
    level = max(level_min, level)
    if level_max is not None:
        level = min(level_max, level)
    unit = interfaces.UNITS.get(
        system,
        {}).get(dimension, [(None,)])[level][0]
    return unit


def system_for_unit(unit_name):
    if unit_name in interfaces.METRICS:
        return interfaces.SYSTEM_METRIC
    elif unit_name in interfaces.IMPERIALS:
        return interfaces.SYSTEM_IMPERIAL
