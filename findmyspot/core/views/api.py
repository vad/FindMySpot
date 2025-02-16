from django.contrib.gis.geos.point import Point
from django.http import HttpResponse
from vectorformats.Formats import Django, GeoJSON

from annoying.decorators import ajax_request


from ..models import HaitiHospitals
from ..forms import HaitiHospitalsForm

#DATA = u"""{"crs": null, "type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [-8059351.285663681, 2099199.355282287]}, "type": "Feature", "id": 26359, "properties": {"id": 26359, "name": "MDM"}}]}"""


def get_hospitals(request):
    qs = HaitiHospitals.objects.exclude(the_geom=None)
    djf = Django.Django(geodjango="the_geom",
                        properties=['id', 'name', 'description', 'hours'])
    geoj = GeoJSON.GeoJSON()
    geojson_output = geoj.encode(djf.decode(qs))
    response = HttpResponse(mimetype="application/json")
    response.write(geojson_output)

#    response.write(DATA)
    return response


@ajax_request
def edit_hospital(request, id_):
    if request.method == 'POST':
        form = HaitiHospitalsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            del data['lat'], data['lon']
            try:
                current_obj = HaitiHospitals.objects.get(id=id_)
            except HaitiHospitals.DoesNotExist:
                return {'success': False}

            current_data = dict([(name, value) for name, value in
                current_obj.__dict__.items() if not name.startswith('_')])
            current_data.update(data)
            if current_obj:
                print current_data
                obj = HaitiHospitals(**current_data)
                obj.save(force_update=True)
                return {'success': True}
    return {'success': False}


@ajax_request
def add_hospital(request):
    if request.method == 'POST':
        form = HaitiHospitalsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            lat = data['lat']
            lon = data['lon']
            if not (lat and lon):
                return {'success': False, 'error': 'Lat or long are empty'}

            del data['lat'], data['lon']
            data['the_geom'] = Point(lon, lat, srid=900913)

            obj = HaitiHospitals.objects.create(**data)
            return {'success': True, 'id': obj.pk}
    return {'success': False}


@ajax_request
def delete_hospital(request, id_):
    if request.method == 'POST':
        params_id = int(id_)
        try:
            hospital = HaitiHospitals.objects.get(id=params_id)
            hospital.delete()
        except:
            return {'success': False}
        return {'success': True}
    return {'success': False}
