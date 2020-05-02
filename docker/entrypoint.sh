#!/bin/sh
set -e

if [ -z "${JACKETT}" ]; then
    JACKETT="jackett-prod:9117"
else
    JACKETT=${JACKETT}
fi

if [ -z "${MEDIASTRENDS_CACHE_TIME}" ]; then
    CACHE_TIME=3600*6
else
    CACHE_TIME=${MEDIASTRENDS_CACHE_TIME}
fi

if [ -f 'compute_movie_trends' ]; then
    ts_last_run=`stat -c '%Z' compute_movie_trends`
    ts_now=`date +%s`
    ts_expiration=$(($ts_last_run+$CACHE_TIME))
    if [ $ts_now -ge $ts_expiration ]; then
        echo "Cache expired..."
        make clean
    fi
else 
    make clean
fi


# check for the expected command
if [ "$1" = 'stats_movie_torrents' ] \
    || [ "$1" = 'add_movie_torrents' ] \
    || [ "$1" = 'compute_movie_trends' ] \
    || [ "$1" = 'get_movie_trends' ]; then
    mediastrends database create
    # exec make "$@"
    CMD="./wait-for-it.sh $JACKETT -- $CMD make $@"
else
    CMD="$@"
fi

exec $CMD
