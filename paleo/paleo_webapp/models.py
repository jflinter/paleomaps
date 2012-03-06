from django.db import models
from django.contrib import admin
import requests
from django.utils import simplejson as json
import oauth2
import urllib
import urllib2
from settings import YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET, YELP_TOKEN, YELP_TOKEN_SECRET

def yelp_request(path, options={}):
  encoded_params = ''
  if options:
    encoded_params = urllib.urlencode(options)
  url = 'http://api.yelp.com/v2/%s?%s' % (path, encoded_params)
  consumer = oauth2.Consumer(YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET)
  oauth_request = oauth2.Request('GET', url, {})
  oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                        'oauth_timestamp': oauth2.generate_timestamp(),
                        'oauth_token': YELP_TOKEN,
                        'oauth_consumer_key': YELP_CONSUMER_KEY})
  token = oauth2.Token(YELP_TOKEN, YELP_TOKEN_SECRET)
  oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
  signed_url = oauth_request.to_url()
  return requests.get(signed_url);


class Place(models.Model):
  name = models.CharField(max_length=200)
  yelp_id = models.CharField(max_length=200, blank=True)
  yelp_phone_number = models.CharField(max_length=30, blank=True)
  yelp_rating = models.CharField(max_length=10, blank=True)
  yelp_review_count = models.CharField(max_length=10, blank=True)
  yelp_url = models.URLField(max_length=200, blank=True)
  yelp_image_rating_url = models.URLField(max_length=200, blank=True)
  location = models.CharField(max_length=200, blank=True)
  latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
  longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
  description = models.TextField(blank=True)
  
  def __unicode__(self):
    return self.name
  
  def refresh_yelp_info(self):
    if (self.latitude and self.longitude):
      yelp_response = yelp_request('search', {'ll' : str(self.latitude)+","+str(self.longitude), 'limit' : 1, 'term' : self.name})
      if yelp_response.status_code == 200:
        y = json.loads(yelp_response.text)
        if y['total'] > 0:
          self.yelp_id = y['businesses'][0]['id']
    if (self.yelp_id):
      yelp_response = yelp_request('business/'+str(self.yelp_id))
      y = json.loads(yelp_response.text)
      if y['is_closed']:
        return False
      phone = y['display_phone']
      if phone.startswith('+'):
        phone = phone[1+phone.find('-'):]
      self.yelp_phone_number = phone
      self.yelp_rating = y['rating']
      self.yelp_review_count = y['review_count']
      self.yelp_url = y['url']
      self.yelp_image_rating_url = y['rating_img_url_small']
      location = y['location']
      self.location = ', '.join([', '.join(location['address']), location['city'], location['state_code'], location['postal_code']])
      self.latitude = y['location']['coordinate']['latitude']
      self.longitude = y['location']['coordinate']['longitude']
    return True
    
  def refresh_google_info(self):
    success = True
    if not self.latitude or not self.longitude:
      success = False
      json_response = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+self.location+'&sensor=false')
      if json_response.status_code == 200:
        r = json.loads(json_response.text)
        if r['status'] == 'OK':
          self.location = str.join(r['results'][0]['formatted_address'], ', ')
          self.latitude = r['results'][0]['geometry']['location']['lat']
          self.longitude = r['results'][0]['geometry']['location']['lng']
          success = True
    return success
      
  def save(self, *args, **kwargs):
    if self.refresh_google_info() and self.refresh_yelp_info():
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
      ('Location information', {'fields': ['latitude', 'longitude'], 'classes': ['collapse']}),
      ('Yelp information', {'fields': ['yelp_id', 'yelp_phone_number', 'yelp_rating', 'yelp_review_count', 'yelp_url', 'yelp_image_rating_url'], 'classes': ['collapse']}),
  ]    
  inlines = [MenuItemInline]

admin.site.register(Place, PlaceAdmin)