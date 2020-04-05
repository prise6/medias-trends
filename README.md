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

[ygg]
scheme=http
domain=ygg.peer2peer.cc
port=8080
netloc=${domain}:${port}
path=
rss_movies=
rss_series=

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
```

user config file have to be named with this pattern: `mediastrends.MODE.ini`, `MODE` is the value of `MEDIASTRENDS_MODE` global var.

`mediastrends` look for user config in these directory:

1. `$MEDIASTRENDS_DIRCONF` if set
2. `.` current directory
3. `~` home directory
4. `/etc/mediastrends` directory

