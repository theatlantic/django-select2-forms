try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For Python <3.8, fallback to importlib_metadata backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version('django-select2-forms')
except PackageNotFoundError:
    __version__ = None

