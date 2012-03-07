from django.conf.urls.defaults import patterns, include, url
from paleo_webapp.views import home, get_all_places, menu_for_place, add_place

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^get_all_places$', get_all_places),
    url(r'^menu_for_place$', menu_for_place),
    url(r'^add_place$', add_place),
)
