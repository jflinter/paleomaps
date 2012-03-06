import os
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from paleo_webapp.models import Place

for place in Place.objects.all():
  place.save()