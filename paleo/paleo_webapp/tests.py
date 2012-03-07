"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import Place, MenuItem
from views import add_place
from django.utils import unittest
from django.http import (QueryDict, HttpResponse, SimpleCookie, BadHeaderError,
        parse_cookie, HttpRequest)
from django.test.client import Client

'''class ModelLocation(unittest.TestCase):
  def test_bad_google_location(self):
    place = Place()
    place.name = "test place"
    place.location = ''
    place.save()
    self.assertEqual(len(Place.objects.all()), 0)
  def test_good_google_location_and_yelp(self):
    place = Place()
    place.name = "Whole Foods"
    place.location = '1240 Yale St, Santa Monica, CA 90404'
    place.save()
    self.assertEqual(place.yelp_id, 'whole-foods-santa-monica')
    self.assertEqual(len(Place.objects.all()), 1)
  def add_new_place(self):
    request.POST = "{'description': [''], 'name': ['Chipotle Mexican Grill'], 'location': ['1074 Broxton Avenue, Los Angeles, CA 90024, United States']}"
    add_place(request)
    print "testing"
    self.assertEqual(len(Place.objects.all()), 1)
'''
class ViewTestCase(unittest.TestCase):
    def test_add_new_place(self):
      """testing adding stuff"""
      client = Client()
      response = client.post('/add_place', {u'description': '', u'name': u'Chipotle Mexican Grill', u'menu_items': [{u'name': u'ipod', u'description': u'fancy'}], u'location': u'1074 Broxton Avenue, Los Angeles, CA 90024, United States'})
      self.assertEqual(len(Place.objects.all()), 1)
      self.assertEqual(len(MenuItem.objects.all()), 1)