from mediastrends.torrent.Torrent import Torrent
from .YggPage import YggPage


class YggTorrent(Torrent):
    pass


#
# use python way to create "classmethod"
#

def yggtorrent_from_yggpage(ygg_page: YggPage):
    return YggTorrent(
        hash_info = ygg_page.hash_info,
        name = ygg_page.name,
        pub_date = ygg_page.pub_date,
        size = ygg_page.size
    )
    