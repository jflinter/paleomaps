"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import Place

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class ModelLocation(TestCase):
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
    self.assertEqual(place.yelp_id, 'hdQJrF3Fw_KrEaDywC3tyg')
    self.assertEqual(len(Place.objects.all()), 1)