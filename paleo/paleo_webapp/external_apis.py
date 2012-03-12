from django.utils import simplejson as json
import oauth2
import urllib
import urllib2
from settings import YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET, YELP_TOKEN, YELP_TOKEN_SECRET, GOOGLE_API_KEY
import requests

def get_yelp_request(path, options={'callback' : 'cb'}):
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
  return signed_url

def google_place_details_search(reference):
  encoded_params = urllib.urlencode({'reference': reference, 'sensor': 'false', 'key': GOOGLE_API_KEY})
  url = 'https://maps.googleapis.com/maps/api/place/details/json?{0}'.format(encoded_params)
  json_response = requests.get(url)
  if json_response.status_code == 200:
    r = json.loads(json_response.text)
    if r['status'] == 'OK':
      return r['result']
  return None

def google_location_search(location, num_results=1):
  encoded_params = urllib.urlencode({'address': location, 'sensor': 'false'})
  url = 'http://maps.googleapis.com/maps/api/geocode/json?{0}'.format(encoded_params)
  json_response = requests.get(url)
  if json_response.status_code == 200:
    r = json.loads(json_response.text)
    if r['status'] == 'OK':
      return r['results'][:num_results]
  return None

def google_place_search(name, latitude, longitude, radius=10000, num_results=1):
  encoded_params = urllib.urlencode({'location': '%s,%s'%(latitude, longitude), 'radius':radius, 'name':name, 'types': 'food', 'key': GOOGLE_API_KEY, 'sensor': 'false'})
  json_response = requests.get(url)
  if json_response.status_code == 200:
    r = json.loads(json_response.text)
    if r['status'] == 'OK':
      results = filter(lambda g: g['name'] in name, r['results'])
      return results[:num_results]
  return None

def google_place_and_location_search(name, latitude, longitude, location='', radius=10000, num_results=1):
  #do a normal place search based on lat/lng
  #for each place, take the vicinity and do a location search on it
  #set the place's returned lat/lng to the location search's lat/lng
  results = None
  encoded_params = urllib.urlencode({'location': '%s,%s'%(latitude, longitude), 'radius':radius, 'name':name, 'types': 'food', 'key': GOOGLE_API_KEY, 'sensor': 'false'})
  url = 'https://maps.googleapis.com/maps/api/place/search/json?{0}'.format(encoded_params)
  json_response = requests.get(url)
  if json_response.status_code == 200:
    r = json.loads(json_response.text)
    if r['status'] == 'OK':
      results = filter(lambda g: g['name'] in name, r['results'])
      results = results[:num_results]
  if (results):
    for result in results:
      if (not location) or num_results > 1:
        place_details = google_place_details_search(result['reference'])
        address = place_details['formatted_address']
      else: address = location
      location_search_result = google_location_search(address)
      if location_search_result:
        latitude = location_search_result[0]['geometry']['location']['lat']
        longitude = location_search_result[0]['geometry']['location']['lng']
        result['geometry']['location']['lat'] = latitude
        result['geometry']['location']['lng'] = longitude
    return results
  return None

def yelp_place_search(name, latitude, longitude, numResults=1):
  params = {'ll': '%d,%d'%(latitude, longitude), 'radius_filter':30000, 'category_filter': 'food,restaurants', 'term':name}
  url = get_yelp_request('search', params)
  json_response = requests.get(url)
  if json_response.status_code == 200:
    r = json.loads(json_response.text)
    return r['businesses'][:numResults]
  return None