from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place, MenuItem, Chain
from django.core import serializers
from django.template import RequestContext
import django.utils.simplejson as json
from external_apis import get_yelp_request, google_location_search, google_place_search, yelp_place_search

def home(request):
  return render_to_response('home.html', RequestContext(request))
  
def get_all_places(request):
  data = serializers.serialize("json", Place.objects.all())
  return HttpResponse(data, mimetype="application/json")
  
def menu_for_place(request):
  chain = Chain.objects.get(pk=request.GET['chain_pk'])
  data = serializers.serialize("json", MenuItem.objects.filter(chain = chain))
  return HttpResponse(data, mimetype="application/json")

def add_menu_item(request):
  data = request.POST
  chain = Chain.objects.get(pk=data['chain_pk'])
  menuitem, created = MenuItem.objects.get_or_create(name=data['menu_item_name'], chain=chain, defaults={'description': data['menu_item_description']})
  data = serializers.serialize("json", [menuitem])
  return HttpResponse(data, mimetype="application/json")
  
def add_place(request):
  data = request.POST
  name = data.get('name')
  is_chain = data.get('is_chain') in ["true", "True"]
  latitude = data.get('latitude')
  longitude = data.get('longitude')
  location = data.get('location')
  if latitude and longitude and name:
    chain, chain_created = Chain.objects.get_or_create(name = name)
    results = google_place_search(name, latitude, longitude, radius=500, num_results=1)
    if results:
      google_id = results[0]['id']
      description = data.get('description')
      place, place_created = Place.objects.get_or_create(google_id = google_id, defaults={'name': name, 'latitude': latitude, 'longitude': longitude, 'chain': chain, 'location': location, 'description': description})
      menuitems = json.loads(data.get('menu_items'))
      for item in menuitems:
        menuitem = MenuItem.objects.get_or_create(name=item['name'], chain=chain, defaults={'description': item['description']})
      places = [place]
      if is_chain:
        results = google_place_search(place.name, place.latitude, place.longitude, num_results=50)
        for result in results:
          defaults = {'name': result['name'], 'latitude': result['geometry']['location']['lat'], 'longitude': result['geometry']['location']['lng'], 'chain': chain, 'location': result['vicinity']}
          chain_place, chain_place_created = Place.objects.get_or_create(google_id = result['id'], defaults=defaults)
          if chain_place_created: places.append(chain_place)
      serialized_places = json.loads(serializers.serialize("json", places))
      response = {'places': serialized_places, 'added': place_created}
      return HttpResponse(json.dumps(response), mimetype="application/json")
  return HttpResponse(json.dumps({'error' : 'place not saved'}), mimetype="application/json")
  
def get_yelp_request_url(request):
  data = request.POST
  business_pk = data.get('business_pk')
  yelp_id = data.get('yelp_id')
  if not yelp_id:
    place = Place.objects.get(pk=business_pk)
    if not place.yelp_id:
      place.refresh_yelp_info()
    yelp_id = place.yelp_id
  if yelp_id:
    yelp_url = get_yelp_request('business/'+yelp_id)
    return HttpResponse(json.dumps({'yelp_url' : yelp_url}), mimetype="application/json")
  else:
    return HttpResponse(json.dumps({'error' : 'yelp id not found'}), mimetype="application/json")
  