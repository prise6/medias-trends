ARG BASE_CONTAINER=python:3.7-buster
FROM $BASE_CONTAINER

ENV USERNAME=mediastrends
ARG PUID=1001
ARG PGID=1001
ARG WORKDIR=/app
ARG VERSION=0.1.1

WORKDIR $WORKDIR
ENV WORKDIR=$WORKDIR
ENV MEDIASTRENDS_DIRCONF=$WORKDIR

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

COPY ./dist/mediastrends-$VERSION-py3-none-any.whl .

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
	apt-get install --no-install-recommends --yes python3-pandas && \
	rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages

RUN pip install --upgrade pip && \
    pip install mediastrends-$VERSION-py3-none-any.whl && \
    pip install git+git://github.com/platelminto/parse-torrent-name.git@d3dbf4c7dcc30990b10e88e93596ca1e8afa2c8b#egg=parse-torrent-name && \
    rm -f *.whl

RUN groupadd --gid $PGID $USERNAME \
    && useradd --uid $PUID --gid $PGID -d $WORKDIR $USERNAME \
    && chown -R $PUID:$PGID $WORKDIR

RUN mkdir -p $WORKDIR/scripts $WORKDIR/logs

COPY scripts/add_movie_torrents.py scripts/stats_movie_torrents.py scripts/
COPY Makefile .

ENTRYPOINT ["/tini", "--", "/entrypoint.sh"]

CMD ["get_movie_trends"]
