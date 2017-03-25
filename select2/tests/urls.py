import django
from django.conf.urls import include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    url(r"^select2/", include("select2.urls")),
]

if django.VERSION < (1, 9):
    urlpatterns += [url(r'^admin/', include(admin.site.urls))]
else:
    urlpatterns += [url(r'^admin/', admin.site.urls)]

try:
    import grappelli.urls
except ImportError:
    pass
else:
    urlpatterns += [url(r"^grappelli/", include(grappelli.urls))]
