import imdb


def get_imdb_access(**kwargs):
    kwargs['reraiseExceptions'] = True
    return imdb.IMDb(**kwargs)


def get_imdb_resource(type_: str = 'movie', id_: int = None, imdb_access=None):
    if id_ is None:
        raise ValueError("Id must be given")
    if imdb_access is None:
        imdb_access = get_imdb_access()
    if type_ == 'movie':
        return imdb_access.get_movie(id_, info=['main'])
