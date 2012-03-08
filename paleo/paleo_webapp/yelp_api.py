from django.utils import simplejson as json
import oauth2
import urllib
import urllib2
from settings import YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET, YELP_TOKEN, YELP_TOKEN_SECRET

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
  
  
  '''y = json.loads(yelp_response.text)
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
  return HttpResponse(json.dumps({'successs' : success}), mimetype="application/json")'''