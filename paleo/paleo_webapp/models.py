from django.db import models
from django.contrib import admin
import json
import requests
from external_apis import get_yelp_request, google_location_search
from djangotoolbox.fields import ListField, DictField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager
from pymongo import Connection, GEO2D
from django.db.models.signals import post_syncdb
from settings import DATABASES

def create_geo_index(sender=None, **kwargs):
  options = DATABASES['default']
  if options['USER'] and options['PASSWORD']:
    uri = 'mongodb://{0}:{1}@{2}:{3}/{4}'.format(options['USER'], options['PASSWORD'], options['HOST'], options['PORT'], options['NAME'])
  else:
    uri = 'mongodb://{0}:{1}/{2}'.format(options['HOST'], options['PORT'], options['NAME'])
  db = Connection(uri)[options['NAME']]
  db.paleo_webapp_place.create_index([("latlng", GEO2D)])

post_syncdb.connect(create_geo_index)

class Chain(models.Model):
  name = models.CharField(max_length=200)
  menu_items = ListField(EmbeddedModelField("MenuItem"))
  def __unicode__(self):
    return self.name

class MenuItem(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  def __unicode__(self):
    return self.name

class Place(models.Model):
  objects = MongoDBManager()
  name = models.CharField(max_length=200)
  yelp_id = models.CharField(max_length=200, blank=True)
  google_id = models.CharField(max_length=1000, blank=True)
  chain = EmbeddedModelField('Chain')
  location = models.CharField(max_length=200, blank=True)
  latlng = DictField(models.FloatField)
  description = models.TextField(blank=True)
  
  def __unicode__(self):
    return self.name
  
  def refresh_yelp_info(self):
    if (self.latlng):
      yelp_response = requests.get(get_yelp_request('search', {'ll' : str(self.latlng['latitude'])+","+str(self.latlng['longitude']), 'limit' : 1, 'term' : self.name}))
      print yelp_response.text, yelp_response.status_code
      if yelp_response.status_code == 200:
        y = json.loads(yelp_response.text)
        if y['total'] > 0:
          self.yelp_id = y['businesses'][0]['id']
          if (self.yelp_id):
            self.save() # Call the "real" save() method.
            return True
    return False
    
  def refresh_google_info(self):
    success = True
    if not self.latitude or not self.longitude:
      success = False
      if self.location:
        results = google_location_search(self.location)
        if results:
          self.location = results[0]['formatted_address']
          self.latitude = results[0]['geometry']['location']['lat']
          self.longitude = results[0]['geometry']['location']['lng']
          success = True
    return success

class PlaceAdmin(admin.ModelAdmin):
  fieldsets = [
      (None,               {'fields': ['name', 'location', 'description']}),
      ('Yelp information', {'fields': ['yelp_id'], 'classes': ['collapse']}),
  ]    
#admin.site.register(MenuItem)
#admin.site.register(Place, PlaceAdmin)