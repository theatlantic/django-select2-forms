import django
from django.urls import include, re_path
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    re_path(r"^select2/", include("select2.urls")),
    re_path(r'^admin/', admin.site.urls)
]

try:
    import grappelli.urls
except ImportError:
    pass
else:
    urlpatterns += [re_path(r"^grappelli/", include(grappelli.urls))]
