#!/bin/sh
set -e

# check for the expected command
if [ "$1" = 'stats_movie_torrents' ] \
    || [ "$1" = 'add_movie_torrents' ] \
    || [ "$1" = 'compute_movie_trends' ] \
    || [ "$1" = 'get_movie_trends' ] \
    || [ "$1" = 'clean' ]; then
    exec mediastrends database create
    exec make "$@"
    exit
fi

exec "$@"
