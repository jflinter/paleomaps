from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place, MenuItem
from django.core import serializers
from django.template import RequestContext
import json
from yelp_api import get_yelp_request

def home(request):
  return render_to_response('home.html', RequestContext(request))
  
def get_all_places(request):
  data = serializers.serialize("json", Place.objects.all())
  return HttpResponse(data, mimetype="application/json")
  
def menu_for_place(request):
  place = Place.objects.get(pk=request.GET['pk'])
  data = serializers.serialize("json", MenuItem.objects.filter(place = place))
  return HttpResponse(data, mimetype="application/json")
  
def add_place(request):
  data = request.POST
  place = Place()
  stuff = json.loads(data.lists()[0][0])
  place.location = stuff['location']
  place.name = stuff['name']
  place.description = stuff['description']
  menuitems = stuff['menu_items']
  success = place.save()
  for item in menuitems:
    print item
    menuitem = MenuItem()
    menuitem.place = place
    menuitem.name = item['name']
    menuitem.description = item['description']
    menuitem.save()
  if (success):
    response_data = serializers.serialize("json", place)
    return HttpResponse(response_data, mimetype="application/json")
  else: return HttpResponse(json.dumps({'error' : 'place not saved'}), mimetype="application/json")
  
def get_yelp_request_url(request):
  data = request.GET
  print data
  business_id = data.get('business_id')
  yelp_url = get_yelp_request('business/'+business_id)
  return HttpResponse(json.dumps({'yelp_url' : yelp_url}), mimetype="application/json")