from django.db import models
from django.contrib import admin
import json
import requests
from yelp_api import get_yelp_request


class Place(models.Model):
  name = models.CharField(max_length=200)
  yelp_id = models.CharField(max_length=200, blank=True)
  location = models.CharField(max_length=200, blank=True)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
  description = models.TextField(blank=True)
  
  def __unicode__(self):
    return self.name
  
  def refresh_yelp_info(self):
    if (self.latitude and self.longitude):
      yelp_response = requests.get(get_yelp_request('search', {'ll' : str(self.latitude)+","+str(self.longitude), 'limit' : 1, 'term' : self.name}))
      if yelp_response.status_code == 200:
        y = json.loads(yelp_response.text)
        if y['total'] > 0:
          self.yelp_id = y['businesses'][0]['id']
          if (self.yelp_id):
            return True
    return False
    
  def refresh_google_info(self):
    success = True
    if not self.latitude or not self.longitude:
      success = False
      if self.location:
        json_response = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+self.location+'&sensor=false')
        if json_response.status_code == 200:
          print json_response
          r = json.loads(json_response.text)
          if r['status'] == 'OK':
            self.location = (r['results'][0]['formatted_address'])
            self.latitude = r['results'][0]['geometry']['location']['lat']
            self.longitude = r['results'][0]['geometry']['location']['lng']
            success = True
    return success
      
  def save(self, *args, **kwargs):
    if self.refresh_google_info() and self.refresh_yelp_info():
      super(Place, self).save(*args, **kwargs) # Call the "real" save() method.
      return True
    else: return False

class MenuItem(models.Model):
  place = models.ForeignKey(Place)
  name = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  def __unicode__(self):
    return self.name

class MenuItemInline(admin.TabularInline):
  model = MenuItem
  extra = 3

class PlaceAdmin(admin.ModelAdmin):
  fieldsets = [
      (None,               {'fields': ['name', 'location', 'description']}),
      ('Location information', {'fields': ['latitude', 'longitude'], 'classes': ['collapse']}),
      ('Yelp information', {'fields': ['yelp_id'], 'classes': ['collapse']}),
  ]    
  inlines = [MenuItemInline]

admin.site.register(Place, PlaceAdmin)