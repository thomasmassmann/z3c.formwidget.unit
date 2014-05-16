# -*- coding: utf-8 -*-

# zope imports
from z3c.form.interfaces import ITextWidget


class IUnitWidget(ITextWidget):
    """Base unit widget."""


class ILengthWidget(IUnitWidget):
    """Unit widget for 'lenght' dimensions."""


class IAreaWidget(IUnitWidget):
    """Unit widget for 'area' dimensions."""
