try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^fetch_items/(?P<app_label>[^\/]+)/(?P<model_name>[^\/]+)/(?P<field_name>[^\/]+)/$',
        'select2.views.fetch_items', name='select2_fetch_items'),
    url(r'^init_selection/(?P<app_label>[^\/]+)/(?P<model_name>[^\/]+)/(?P<field_name>[^\/]+)/$',
        'select2.views.init_selection', name='select2_init_selection'),
)
