# Medias Trends with Torrents

The idea is to use torrent statistics to define which media (movies, series or other) is in trend.

The first step is to initialize a torrent database. Then, retrieve the statistics (completed, leechers, seeders) and store them. Finally, define which torrents are trending thanks to its statistics.

Each torrent has a status (_new_, _follow_, _unfollow_). These statuses allow you to continue collecting stats or not.

Statistics are collected for torrents with a _new_ and _follow_ status.

By default, a torrent has the status _new_ for three days. It changes to the _follow_ status if it is trending at the end of the _new_ period.

A simple clustering on torrent names allows to attach torrents to a movie (or a series - in dev)


## Package `mediastrends`

### Requirements

* Python >= 3.6
* Linux OS (debian, ubuntu)
* set `MEDIASTRENDS_MODE` global environment variable 
* create configuration file to put in `<project>/mediastrends.MODE.ini`


### CLI

```
> mediastrends
usage: mediastrends [-h] [-v] [-f CONFIG_DIR] [-m MODE]
                    {database,torrents,movies} ...

CLI to interact with mediastrends'tasks 

The logic steps to update database are:
    1. torrents add
    2. torrents stats
    3. torrents trends compute
    4. torrents status
    5. torrents trends get

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Set mediastrend logger level, 0 to 5.
  -f CONFIG_DIR, --config-dir CONFIG_DIR
                        Configuration directory. Load mediastrends.MODE.ini
  -m MODE, --mode MODE  Mode. Override MEDIASTRENDS_MODE environment

Top level commands:
  {database,torrents,movies}
    database            Commands on database
    torrents            Commands on torrent
    movies              Commands on movies
```

### Installation

```
pip install git+https://github.com/prise6/medias-trends@master
```

### Config file

User have to override some values of default config:

Content of mediastrends.ini (default config)
```ini
[directory]
base=
data=
log=${base}/logs
sqlite=

[db]
database=sqlite

[sqlite]
path=${directory:sqlite}/database.db
backup_dir=${directory:data}

[indexers]
indexer_file=

[trackers]
tracker_file=

[requests]
user_agent=
batch_size=50

[retry]
tries=10
delay=5

[stats_manager]
new_delay=3

[trends]
tau=0.2

[jackettapi]
scheme=http
domain=jackett
port=9117
netloc=${domain}:${port}
path=api/v2.0/indexers/{indexer}/results/torznab/api
apikey=

```

user config file have to be named with this pattern: `mediastrends.MODE.ini`, `MODE` is the value of `MEDIASTRENDS_MODE` global var.

`mediastrends` look for user config in these directory:

1. `$MEDIASTRENDS_DIRCONF` if set
2. `.` current directory
3. `~` home directory
4. `/etc/mediastrends` directory


### YAML file

#### indexers.yaml

This file lists indexer website to collect new torrents.

fill the filepath of this file in config file:
```ini
[indexers]
indexer_file=
```

Example of content of the file:

```yaml
indexers:
  indexer_1: # /!\ must be a tracker known by jackett
    cat_1:
      active: True
      action: search
      params:
        cat: 2000
    cat_2:
      active: True
      action: search
      params:
        cat: 5000
  indexer_2:
    movies:
      active: True
      action: search
```

#### trackers.yaml

This file lists bittorrent tracker to collect statistics from torrents.

fill the filepath of this file in config file:
```ini
# ...
[trackers]
tracker_file=
# ...
```

Example of content of the file:

```yaml
trackers:
  tracker_1:
    active: True
    scheme: http
    netloc: domain:port
    path: 
  
  tracker_2:
    active: True
    scheme: udp
    netloc: domain:port
    path: 
```

### Usage

_Full pipeline only working with movies for now_


#### With CLI

```bash
# add torrents to DB
mediastrends torrents add -c movies -i indexer_1
mediastrends torrents add -c movies -i indexer_2
# collect statistics for new and followed torrents
mediastrends torrents stats -c movies -t tracker_1
mediastrends torrents stats -c movies -t tracker_2
# compute if new or follow torrents is still trending
mediastrends torrents trends compute -c movies
# compute new statuses based on new data
mediastrends torrents status -c movies
# get trending torrents
mediastrends torrents trends get -c movies
# compute movies trends based on torrents data
mediastrends movies compute
# get trending movies
mediastrends movies get
```

#### Makefile as a DAG

These methods need to have the entire repo (not only the package).

_For movie pipeline_

```bash
# reset old runs
make clean
# get trending movies
make get_movie_trends
# see Makefile file for more details
```

#### Docker

Docker image of this project: [prise6/mediastrends](https://hub.docker.com/r/prise6/mediastrends)

Use latest version, available for amd64, armv7.

This image will use an entrypoint to make mediastrends use easier. See dockerhub page for more details.


#### Airflow

_To-do_


## Disclaimer

One main goal of this project is learning:

* more *advanced* topics in Python:
  * linting (flake8)
  * unittest and mocking
  * typing
  * packaging
  * cli with argparse
  * peewee ORM
* github action (see .github/package.yaml)
* airflow
* bittorent protocol
* vscode + remote container dev with python

## Nex steps

* implements a publisher package (create static website)
* Develop serie pipeline
* Use airflow instead of Make
* ...

## Output example

_Old run_

```
          Fantasy Island
Year:2020
id:0983946
Nombre de torrents:2

          Dangerous Lies
Year:2020
id:10183816
Nombre de torrents:3

          Rich in Love
Year:2020
id:10329566
Nombre de torrents:1

          Rendez-vous chez les Malawas
Year:2019
id:10537978
Nombre de torrents:1

          Dreamkatcher
Year:2020
id:10553210
Nombre de torrents:1
```

## License

GNU GPLv3

This project use mainly [peewee](https://github.com/coleifer/peewee) under MIT license, [jackett](https://github.com/Jackett/Jackett) under GNU GPLv2.
