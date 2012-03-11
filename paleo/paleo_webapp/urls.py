from django.conf.urls.defaults import patterns, include, url
from paleo_webapp.views import home, get_all_places, menu_for_place, add_place, add_menu_item, get_yelp_request_url

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^get_all_places$', get_all_places),
    url(r'^menu_for_place$', menu_for_place),
    url(r'^add_place$', add_place),
    url(r'^add_menu_item$', add_menu_item),
    url(r'^get_yelp_url$', get_yelp_request_url),
)
