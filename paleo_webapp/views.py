from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from paleo_webapp.models import Place
from django.core import serializers

def home(request):
  return render_to_response('home.html')
  
def get_all_places(request):
  data = serializers.serialize("json", Place.objects.all())
  return HttpResponse(data, mimetype="application/json")