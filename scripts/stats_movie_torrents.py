import os
import logging
import mediastrends
import mediastrends.tasks.torrents as tasks

dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(mediastrends.config.get('directory', 'logs'), 'mediastrends.txt'),
            'mode': 'a',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'mediastrends': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
logging.config.dictConfig(dict_config)

def main():
    for tracker, conf in mediastrends.trackers_config.items():
        tasks.torrents_stats(False, tracker_name=tracker, category=["movies"])
        
if __name__ == '__main__':
    main()