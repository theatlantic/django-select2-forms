try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

import select2.views


urlpatterns = [
    url(r'^fetch_items/(?P<app_label>[^\/]+)/(?P<model_name>[^\/]+)/(?P<field_name>[^\/]+)/$',
        select2.views.fetch_items, name='select2_fetch_items'),
    url(r'^init_selection/(?P<app_label>[^\/]+)/(?P<model_name>[^\/]+)/(?P<field_name>[^\/]+)/$',
        select2.views.init_selection, name='select2_init_selection'),
]
