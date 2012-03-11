from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place, MenuItem, Chain
from django.core import serializers
from django.template import RequestContext
import django.utils.simplejson as json
from external_apis import get_yelp_request, google_location_search

def home(request):
  return render_to_response('home.html', RequestContext(request))
  
def get_all_places(request):
  data = serializers.serialize("json", Place.objects.all())
  return HttpResponse(data, mimetype="application/json")
  
def menu_for_place(request):
  chain = Chain.objects.get(pk=request.GET['chain_pk'])
  data = serializers.serialize("json", MenuItem.objects.filter(chain = chain))
  return HttpResponse(data, mimetype="application/json")
  
def add_place(request):
  data = request.POST
  name = data.get('name')
  location = data.get('location')
  if location and name:
    results = google_location_search(location)
    google_location = location
    if results:
      google_location = results['formatted_address']
    description = data.get('description')
    chain, chain_created = Chain.objects.get_or_create(name = name)
    place, place_created = Place.objects.get_or_create(name = name, location= google_location, defaults={'chain': chain, 'description': description})
    success = place.save()
    menuitems = json.loads(data.get('menu_items'))
    for item in menuitems:
      menuitem = MenuItem()
      menuitem.chain = chain
      menuitem.name = item['name']
      menuitem.description = item['description']
      menuitem.save()
    if (success):
      serialized_place = json.loads(serializers.serialize("json", [place]))
      response = {'place_details': serialized_place[0], 'added': place_created}
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
  