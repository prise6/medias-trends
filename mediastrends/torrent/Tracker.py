import urllib.parse


class Tracker:

    def __init__(self, scheme, netloc, path, name):
        self._scheme = scheme
        self._netloc = netloc
        self._path = path
        self._name = name

    @property
    def scheme(self):
        return self._scheme

    @property
    def netloc(self):
        return self._netloc

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return urllib.parse.urlunsplit(
            urllib.parse.SplitResult(self._scheme, self._netloc, self._path, None, None)
        )
