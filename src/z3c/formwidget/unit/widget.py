# -*- coding: utf-8 -*-

# python imports
from pint import UndefinedUnitError
import string

# fanstatic
try:
    from js.bootstrap_select import bootstrap_select
    HAS_BS_SELECT = True
except ImportError:
    HAS_BS_SELECT = False

# zope imports
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import (
    IDataConverter,
    IFieldWidget,
    IFormLayer,
    NO_VALUE,
)
from zope.component import adapter
from zope.interface import (
    implementer,
    implementsOnly,
)
from zope.schema.interfaces import ITextLine

# local imports
from z3c.formwidget.unit import ureg
from z3c.formwidget.unit.i18n import _
from z3c.formwidget.unit import interfaces

SYSTEM_METRIC = 'metric'
SYSTEM_IMPERIAL = 'imperial'

DIMENSION_AREA = 'area'
DIMENSION_LENGTH = 'length'

# Metric length units.
UNIT_M = ('m', u'm', _(u'meter'), None)
UNIT_KM = ('km', u'km', _(u'kilometer'), _(u'1,000 meter'))

# Metric area units.
UNIT_SQM = ('sq_m', u'm²', _(u'square meter'), None)
UNIT_HA = ('ha', u'ha', _(u'hectare'), _(u'10,000 m²'))
UNIT_SQKM = ('sq_km', u'km²', _(u'square kilometer'), _(u'100 ha'))

# Imperial length units.
UNIT_FT = ('ft', u'ft', _(u'foot'), None)
UNIT_YD = ('yd', u'yd', _(u'yard'), _(u'3 feet'))
UNIT_MI = ('mi', u'mi', _(u'mile'), _(u'1,760 yards'))

# Imperial area units.
UNIT_SQFT = ('sq_ft', u'sq ft', _(u'square feet'), None)
UNIT_ACRE = ('acre', u'acre', _(u'acre'), _(u'43,560 sq ft'))
UNIT_SQMI = ('sq_mi', u'sq mi', _(u'square mile'), _(u'640 acres'))

LABELS = {
    SYSTEM_METRIC: _(u'Metric'),
    SYSTEM_IMPERIAL: _(u'Imperial'),
}

UNITS = {
    SYSTEM_METRIC: {
        DIMENSION_AREA: [
            UNIT_SQM,
            UNIT_HA,
            UNIT_SQKM,
        ],
        DIMENSION_LENGTH: [
            UNIT_M,
            UNIT_KM,
        ],
    },
    SYSTEM_IMPERIAL: {
        DIMENSION_AREA: [
            UNIT_SQFT,
            UNIT_ACRE,
            UNIT_SQMI,
        ],
        DIMENSION_LENGTH: [
            UNIT_FT,
            UNIT_MI,
        ],
    },
}

BASE_UNITS = {
    DIMENSION_AREA: UNIT_SQM,
    DIMENSION_LENGTH: UNIT_M,
}


class MultiUnitWidget(TextWidget):
    """Multi Unit Widget based on TextWidget."""
    implementsOnly(interfaces.IUnitWidget)

    klass = u'multiunit-widget'
    value = u''
    unit = None

    unit_systems = (SYSTEM_METRIC, SYSTEM_IMPERIAL)
    preferred_system = SYSTEM_METRIC

    data_header = _(u'Select a unit')
    data_width = '75px'

    _javascript_input = """
jQuery(function(jq){
    jq('#${id}-unit').selectpicker({});
});
    """

    @property
    def unit_dimension(self):
        raise NotImplementedError

    @property
    def widget_value(self):
        self.unit = self.request.get(self.name + '-unit', self.preferred_unit)

        try:
            # unit = getattr(ureg, self.unit)
            base_unit = getattr(ureg, self.base_unit)
        except UndefinedUnitError:
            value = self.value
        else:
            # Do the conversion
            converter = IDataConverter(self)
            value = converter.toFieldValue(self.value)
            unit = self.get_best_unit(value)
            value = value * base_unit
            value = value.to(unit).magnitude
            value = converter.toWidgetValue(value)
        return value

    def render(self):
        if HAS_BS_SELECT:
            bootstrap_select.need()
        return super(MultiUnitWidget, self).render()

    def get_best_unit(self, value):
        level = 0
        if self.unit_dimension == DIMENSION_AREA:
            if value < 1000:
                level = 0
            elif value <= 1000000:
                level = 1
            else:
                level = 2
        elif self.unit_dimension == DIMENSION_LENGTH:
            if value > 400:
                level = 1
        self.unit = UNITS.get(
            self.preferred_system,
            {}).get(self.unit_dimension, [(None,)])[level][0]
        return getattr(ureg, self.unit)

    def extract(self, default=NO_VALUE):
        value = self.request.get(self.name, default)
        unit_name = self.request.get(self.name + '-unit', self.base_unit)
        if unit_name != self.base_unit:
            try:
                unit = getattr(ureg, unit_name)
                base_unit = getattr(ureg, self.base_unit)
            except UndefinedUnitError:
                value = self.field.get(self.context)
            else:
                # Do the conversion
                converter = IDataConverter(self)
                value = converter.toFieldValue(value)
                value = value * unit
                value = value.to(base_unit).magnitude
            value = converter.toWidgetValue(value)
        return value

    def javascript_input(self):
        return string.Template(self._javascript_input).substitute(dict(
            id=self.id,
        ))

    def isSelected(self, key):
        return key == self.unit

    @property
    def base_unit(self):
        return BASE_UNITS.get(self.unit_dimension)[0]

    @property
    def preferred_unit(self):
        return UNITS.get(
            self.preferred_system, {}
        ).get(self.unit_dimension, [(None,)])[0][0]

    def items(self):
        items = []
        for system in self.unit_systems:
            dimensions = UNITS.get(system, None)
            if not dimensions:
                continue
            units = []
            available_units = dimensions.get(self.unit_dimension, [])
            for unit in available_units:
                abbr, label_short, label, info = unit
                subtext = label
                if info:
                    subtext = subtext + ' (%s)' % info
                units.append({
                    'id': abbr,
                    'value': abbr,
                    'content': label_short,
                    'subtext': subtext,
                    'selected': self.isSelected(abbr),
                })

            item = {}
            item['title'] = LABELS.get(system)
            item['member'] = units
            items.append(item)

        return items


class AreaWidget(MultiUnitWidget):
    """Unit widget for 'area' dimensions."""
    implementsOnly(interfaces.IAreaWidget)
    klass = u'area-widget unit-widget'

    @property
    def unit_dimension(self):
        return DIMENSION_AREA


@adapter(ITextLine, IFormLayer)
@implementer(IFieldWidget)
def AreaFieldWidget(field, request):
    """Factory for AreaWidget"""
    return FieldWidget(field, AreaWidget(request))


class LengthWidget(MultiUnitWidget):
    """Unit widget for 'length' dimensions."""
    implementsOnly(interfaces.ILengthWidget)
    klass = u'length-widget unit-widget'

    @property
    def unit_dimension(self):
        return DIMENSION_LENGTH


@adapter(ITextLine, IFormLayer)
@implementer(IFieldWidget)
def LengthFieldWidget(field, request):
    """Factory for LengthWidget"""
    return FieldWidget(field, LengthWidget(request))
