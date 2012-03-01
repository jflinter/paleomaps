from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place, MenuItem
from django.core import serializers
from django.template import RequestContext

def home(request):
  return render_to_response('home.html', RequestContext(request))
  
def get_all_places(request):
  data = serializers.serialize("json", Place.objects.all())
  return HttpResponse(data, mimetype="application/json")
  
def menu_for_place(request):
  place = Place.objects.get(pk=request.GET['pk'])
  data = serializers.serialize("json", MenuItem.objects.filter(place = place))
  return HttpResponse(data, mimetype="application/json")