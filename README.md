# Medias Trends (Torrents)

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
                    {database,torrents} ...

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
  {database,torrents}
    database            Commands on torrent
    torrents            Commands on database
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

This file lists indexer website. 

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

This file lists bittorrent tracker to scrape infos.

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

To Do
