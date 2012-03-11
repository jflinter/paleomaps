from django.db import models
from django.contrib import admin
import json
import requests
from external_apis import get_yelp_request, google_location_search


class Chain(models.Model):
  name = models.CharField(max_length=200)
  def __unicode__(self):
    return self.name

class Place(models.Model):
  name = models.CharField(max_length=200)
  yelp_id = models.CharField(max_length=200, blank=True)
  google_id = models.CharField(max_length=1000, blank=True)
  chain = models.ForeignKey(Chain)
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
            super(Place, self).save() # Call the "real" save() method.
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
      
  def save(self, *args, **kwargs):
    if True:#self.refresh_google_info():
      super(Place, self).save(*args, **kwargs) # Call the "real" save() method.
      return True
    else: return False

class MenuItem(models.Model):
  chain = models.ForeignKey(Chain)
  name = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  def __unicode__(self):
    return self.name

class MenuItemInline(admin.TabularInline):
  model = MenuItem
  extra = 3

class ChainAdmin(admin.ModelAdmin):
  fieldsets = [(None, {'fields': ['name']})]
  inlines = [MenuItemInline]

class PlaceAdmin(admin.ModelAdmin):
  fieldsets = [
      (None,               {'fields': ['name', 'location', 'description']}),
      ('Location information', {'fields': ['latitude', 'longitude'], 'classes': ['collapse']}),
      ('Yelp information', {'fields': ['yelp_id'], 'classes': ['collapse']}),
  ]    

admin.site.register(Place, PlaceAdmin)
admin.site.register(Chain, ChainAdmin)