import argparse
from mediastrends.tasks import *


_ACTIONS_FUNC = {
    'add_torrents': add_torrents,
    'get_stats': get_stats,
    'compute_trending': compute_trending,
    'update_status': update_status,
    'get_trending': get_trending
}


def main(action, **kwargs):

    assert action in _ACTIONS_FUNC.keys()

    _ACTIONS_FUNC.get(action)(**kwargs)

    return


if __name__ == '__main__':


    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title = "title", description= "description", help = "Action on torrents", dest = "action")

    parser_add_torrents = subparsers.add_parser("add_torrents", help = "Add torrents in database")
    parser_add_torrents.add_argument("-c", "--category", help="Torrents category", type=str, nargs = '+', choices = ["movies", "series", "unknown"])
    parser_add_torrents.add_argument("-t", "--tracker-name", help="Tracker name", type=str, choices = ["ygg"])

    parser_get_stats = subparsers.add_parser("get_stats", help = "Save seeders, leechers, completed from tracker")
    parser_get_stats.add_argument("-t", "--tracker-name", help="Tracker name", type=str, choices = ["ygg"])
    parser_get_stats.add_argument("-c", "--category", help="Torrents category", type=str, nargs = '+', choices = ["movies", "series", "unknown"])

    parser_compute_trending = subparsers.add_parser("compute_trending", help = "Compute which torrents are most popular")
    parser_compute_trending.add_argument("-c", "--category", help="Torrents category", type=str, nargs = '+', choices = ["movies", "series", "unknown"])
    parser_compute_trending.add_argument("-di", "--mindate", help="Min datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))
    parser_compute_trending.add_argument("-dx", "--maxdate", help="Max datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))

    parser_update_status = subparsers.add_parser("update_status", help = "Define which torrent are new, to follow and to forget")
    parser_update_status.add_argument("-c", "--category", help="Torrents category", type=str, nargs = '+', choices = ["movies", "series", "unknown"])

    parser_get_trending = subparsers.add_parser("get_trending", help = "Print trending torrents")
    parser_get_trending.add_argument("-c", "--category", help="Torrents category", type=str, nargs = '+', choices = ["movies", "series", "unknown"])
    parser_get_trending.add_argument("-di", "--mindate", help="Min datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))
    parser_get_trending.add_argument("-dx", "--maxdate", help="Max datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))


    args = main_parser.parse_args()

    if args.action:
        main(**vars(args))
    else:
        main_parser.print_help()

    exit()
    