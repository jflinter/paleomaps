from django.db import models
from django.contrib import admin
import requests
import json

class Place(models.Model):
  name = models.CharField(max_length=200)
  yelp_id = models.CharField(max_length=200, blank=True)
  location = models.CharField(max_length=200, blank=True)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
  description = models.TextField(blank=True)
  def __unicode__(self):
    return self.name
  def save(self, *args, **kwargs):
    shouldSave = True
    if not self.latitude or not self.longitude:
      shouldSave = False
      json_response = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+self.location+'&sensor=false')
      if json_response.status_code == 200:
        r = json.loads(json_response.text)
        if r['status'] == 'OK':
          self.location = r['results'][0]['formatted_address']
          self.latitude = r['results'][0]['geometry']['location']['lat']
          self.longitude = r['results'][0]['geometry']['location']['lng']
          shouldSave = True
          if not self.yelp_id:
            yelp_search_url = 'http://api.yelp.com/business_review_search?term='+self.name+'&lat='+str(self.latitude)+'&long='+str(self.longitude)+'&limit=1&ywsid=Kw0AXirx-MVbRRTRfIwX5Q'
            yelp_response = requests.get(yelp_search_url)
            if yelp_response.status_code == 200:
              y = json.loads(yelp_response.text)
              if y['message']['code'] == 0:
                self.yelp_id = y['businesses'][0]['id']
    if shouldSave:
      super(Place, self).save(*args, **kwargs) # Call the "real" save() method.
    

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
      ('Location/Yelp information', {'fields': ['yelp_id', 'latitude', 'longitude'], 'classes': ['collapse']}),
  ]    
  inlines = [MenuItemInline]

admin.site.register(Place, PlaceAdmin)