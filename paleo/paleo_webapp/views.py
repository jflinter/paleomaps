from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place, MenuItem, Chain
from django.core import serializers
from django.template import RequestContext
import django.utils.simplejson as json
from external_apis import get_yelp_request, google_location_search, google_place_search, yelp_place_search, google_place_and_location_search

def home(request):
  return render_to_response('home.html', RequestContext(request))
  
def get_all_places(request):
  data = request.GET
  latitude = data['latitude']
  longitude = data['longitude']
  query_location = {'latitude': float(latitude), 'longitude': float(longitude)}
  places = Place.objects.raw_query({'latlng' : {'$near' : query_location}})
  print "PLACE EXAMPLE", places[0]
  data = serializers.serialize("json", places)
  return HttpResponse(data, mimetype="application/json")
  
def menu_for_place(request):
  chain = Chain.objects.get(name=request.GET['chain_name'])
  data = serializers.serialize("json", chain.menu_items)
  return HttpResponse(data, mimetype="application/json")

def add_menu_item(request):
  data = request.POST
  chain_name=data['chain_name']
  item_name=data['menu_item_name']
  item_desc=data['menu_item_description']
  menuitem = addItem(chain_name, item_name, item_desc)
  data = serializers.serialize("json", [menuitem])
  return HttpResponse(data, mimetype="application/json")

def addItem(chain_name, item_name, item_desc):
  chain = Chain.objects.get(name=chain_name)
  menuitem = MenuItem.objects.create(name=item_name, description=item_desc)
  chain.menu_items.extend([menuitem])
  chain.save()
  return menuitem

def add_place(request):
  data = request.POST
  name = data.get('name')
  is_chain = data.get('is_chain') in ["true", "True"]
  latitude = data.get('latitude')
  longitude = data.get('longitude')
  location = data.get('location')
  if latitude and longitude and name:
    chain, chain_created = Chain.objects.get_or_create(name = name)
    results = google_place_and_location_search(name, latitude, longitude, location=location, radius=500, num_results=1)
    if results:
      google_id = results[0]['id']
      description = data.get('description')
      latlng = {'latitude' : float(results[0]['geometry']['location']['lat']), 'longitude' : float(results[0]['geometry']['location']['lng'])}
      place, place_created = Place.objects.get_or_create(google_id = google_id, defaults={'name': name, 'latlng': latlng, 'chain': chain, 'location': location, 'description': description})
      print place, place_created
      menuitems = json.loads(data.get('menu_items'))
      for item in menuitems:
        addItem(name, item['name'], item['description'])
      if is_chain:
        results = google_place_and_location_search(place.name, place.latlng['latitude'], place.latlng['longitude'], num_results=50)
        for result in results:
          latlng = {'latitude' :result['geometry']['location']['lat'], 'longitude' : result['geometry']['location']['lng']}
          defaults = {'name': result['name'], 'latlng': latlng, 'chain': chain, 'location': result['vicinity']}
          chain_place, chain_place_created = Place.objects.get_or_create(google_id = result['id'], defaults=defaults)
      response = {'added': place_created, 'place_id': place.google_id}
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
  