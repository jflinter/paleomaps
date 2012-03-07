from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place, MenuItem
from django.core import serializers
from django.template import RequestContext
import json

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
  print request.raw_post_data
  data = request.POST
  place = Place()
  stuff = json.loads(data.lists()[0][0])
  print stuff
  place.location = stuff['location']
  place.name = stuff['name']
  place.description = stuff['description']
  print place.location, place.name, place.description
  menuitems = stuff['menu_items']
  success = place.save()
  print "Saved place", success
  for item in menuitems:
    print item
    menuitem = MenuItem()
    menuitem.place = place
    menuitem.name = item['name']
    menuitem.description = item['description']
    menuitem.save()
  return HttpResponse(json.dumps({'successs' : success}), mimetype="application/json")