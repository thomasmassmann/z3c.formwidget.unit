# -*- coding: utf-8 -*-

# python imports
import string

# zope imports
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget, IFormLayer
from zope.component import adapter
from zope.interface import implementer, implementsOnly
from zope.schema.interfaces import ITextLine

# local imports
from z3c.formwidget.multiunit.interfaces import IMultiUnitWidget


class MultiUnitWidget(TextWidget):
    """Multi Unit Widget based on TextWidget."""
    implementsOnly(IMultiUnitWidget)

    klass = u'geoselect-widget'
    value = u''
    center = None

    _javascript_display = """
jQuery(function(jq){
  var mapDiv = jq('<div id="${id}-map" class="map"></div>');
  jq('#${id}').append(mapDiv);

  var center = new google.maps.LatLng(${lat_center}, ${lng_center})
  var myOptions = {
    zoom: ${zoom},
    center: center,
    mapTypeId: google.maps.MapTypeId.TERRAIN,
    mapTypeControl: true,
    disableDoubleClickZoom: true,
    streetViewControl: true
  }

  var map = new google.maps.Map(mapDiv.get(0), myOptions);

  var has_marker = ${has_marker};
  if(has_marker) {
    var myLatlng = new google.maps.LatLng(${lat}, ${lng});
    var marker = new google.maps.Marker({
      position: myLatlng,
      map: map,
    });
  }
});
    """

    _javascript_input = """
jQuery("#${id}").locationPicker({
  defaultLat: '9.784851',
  defaultLng: '-84.116821',
  width: '420px',
  height: '380px'
});
    """

    def render(self):
        return super(MultiUnitWidget, self).render()

    def javascript_display(self):
        lat = lng = 0
        zoom = 1
        has_marker = 0

        if getattr(self, 'zoom', None) is not None:
            zoom = self.zoom

        if self.value is not None:
            lat_lng = self.value.split(',')
            if len(lat_lng) == 2:
                lat = lat_lng[0]
                lng = lat_lng[1]
                has_marker = 1

        if getattr(self, 'center', None) is not None:
            lat_center, lng_center = self.center
        else:
            lat_center = lat
            lng_center = lng

        return string.Template(self._javascript_display).substitute(dict(
            id=self.id,
            has_marker=has_marker, lat=lat, lng=lng,
            lat_center=lat_center, lng_center=lng_center,
            zoom=zoom,
        ))

    def javascript_input(self):
        return string.Template(self._javascript_input).substitute(dict(
            id=self.id,
        ))


@adapter(ITextLine, IFormLayer)
@implementer(IFieldWidget)
def MultiUnitFieldWidget(field, request):
    """Factory for MultiUnitWidget"""
    return FieldWidget(field, MultiUnitWidget(request))
