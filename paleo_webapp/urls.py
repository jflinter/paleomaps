from django.conf.urls.defaults import patterns, include, url
from paleo_webapp.views import home, get_all_places

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^get_all_places$', get_all_places)
)
