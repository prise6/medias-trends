ARG BASE_CONTAINER=python:3.7-buster
FROM $BASE_CONTAINER

ARG USERNAME=mediastrends
ARG USER_UID=1001
ARG USER_GID=$USER_UID
ARG WORKDIR=/app
ARG VERSION=1.0.0

WORKDIR $WORKDIR
ENV WORKDIR=$WORKDIR
ENV MEDIASTRENDS_DIRCONF=$WORKDIR

COPY ./dist/mediastrends-$VERSION-py3-none-any.whl .
 
RUN pip install --upgrade pip && \
    pip install mediastrends-$VERSION-py3-none-any.whl && \
    pip install git+git://github.com/platelminto/parse-torrent-name.git@d3dbf4c#egg=parse-torrent-name && \
    rm -f *.whl

# RUN ln -s /home/$USERNAME/.local/bin/mediastrends /usr/bin/mediastrends

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USER_UID:$USER_GID $WORKDIR

USER $USERNAME

# use entrypoint one day
CMD ["tail", "-f", "/dev/null"]
