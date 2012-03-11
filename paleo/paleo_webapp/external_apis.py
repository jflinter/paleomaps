from django.utils import simplejson as json
import oauth2
import urllib
import urllib2
from settings import YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET, YELP_TOKEN, YELP_TOKEN_SECRET
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
  
def google_location_search(location):
  encoded_params = urllib.urlencode({'address': location, 'sensor': 'false'})
  print encoded_params
  url = 'http://maps.googleapis.com/maps/api/geocode/json?{0}'.format(encoded_params)
  json_response = requests.get(url)
  if json_response.status_code == 200:
    r = json.loads(json_response.text)
    if r['status'] == 'OK':
      return r['results'][0]
  return None