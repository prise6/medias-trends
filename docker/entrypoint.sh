#!/bin/sh
set -e

if [ $(id -u) -eq 0 ]; then
    if ! [ -z "${PUID}" ]; then
        actual_puid=`id -u mediastrends`
        if ! [ $actual_puid -eq ${PUID} ]; then
            echo "Changing uid $actual_puid to ${PUID} ..."
            usermod -u ${PUID} mediastrends
            chown -R mediastrends $WORKDIR
        fi
    fi

    if ! [ -z "${PGID}" ]; then
        actual_pgid=`id -g mediastrends`
        if ! [ $actual_pgid -eq ${PGID} ]; then
            echo "Changing gid $actual_pgid to ${PGID} ..."
            groupmod -g ${PGID} mediastrends
            chgrp -R mediastrends $WORKDIR
        fi
    fi
fi


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
    CMD="./wait-for-it.sh $JACKETT -- mediastrends database create && make $@"
else
    CMD="$@"
fi

if [ $(id -u) -eq 0 ]; then
    exec su - mediastrends -w TZ,MEDIASTRENDS_MODE,PUID,PGID -s /bin/bash -c "$CMD"
else
    exec "$CMD"
fi
