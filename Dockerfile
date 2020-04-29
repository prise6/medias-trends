ARG BASE_CONTAINER=python:3.7-slim-buster
FROM $BASE_CONTAINER

ARG USERNAME=mediastrends
ARG USER_UID=1001
ARG USER_GID=$USER_UID
ARG WORKDIR=/app
ARG VERSION=1.0.0

WORKDIR $WORKDIR
ENV WORKDIR=$WORKDIR
ENV MEDIASTRENDS_DIRCONF=$WORKDIR

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN apt-get update && \
    apt-get install -y --no-install-recommends git libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./dist/mediastrends-$VERSION-py3-none-any.whl .
 
RUN pip install --upgrade pip && \
    pip install Cython==0.29.16 && \
    pip install mediastrends-$VERSION-py3-none-any.whl && \
    pip install git+git://github.com/platelminto/parse-torrent-name.git@d3dbf4c7dcc30990b10e88e93596ca1e8afa2c8b#egg=parse-torrent-name && \
    rm -f *.whl

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USER_UID:$USER_GID $WORKDIR

USER $USERNAME

RUN mkdir -p $WORKDIR/scripts

COPY scripts/add_movie_torrents.py scripts/stats_movie_torrents.py scripts/

ENTRYPOINT ["/tini", "--"]

CMD ["tail", "-f", "/dev/null"]
