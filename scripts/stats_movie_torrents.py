import os
import logging
import mediastrends
import mediastrends.tasks.torrents as tasks

mode = os.getenv('MEDIASTRENDS_MODE')
log_file = os.path.join(mediastrends.config.get('directory', 'logs'), 'mediastrends_' + mode + '.txt')

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
            'filename': log_file,
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