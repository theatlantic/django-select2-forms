import pkg_resources

try:
    __version__ = pkg_resources.get_distribution('django-select2-forms').version
except pkg_resources.DistributionNotFound:
    __version__ = None
