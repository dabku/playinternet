from scrapers import playhuaweib525
from time import sleep, time
from influxdb import InfluxDBClient
import logging
from helpers import set_logger
from os import path
import sys
import json

logger = logging.getLogger()

if __name__ == '__main__':
    script_dir = path.dirname(path.realpath(sys.argv[0]))
    with open(path.join(script_dir,'config_playb525.json'), 'r') as f:
        config = json.load(f)

    set_logger(logger, filename=config['logger']['file_name'], level=config['logger']['level'])
    logger.info('Script started')

    rscraper = playhuaweib525.PlayHuaweiB525(config['router']['ip'])
    client = InfluxDBClient(config['db']['host'], config['db']['port'], config['db']['user'], config['db']['password'],
                            config['db']['db_name'])

    info = rscraper.get_all()

    timestamp = int(time())

    data = [
        {
            'measurement': 'dataUsage',
            'tags': {
                'source': 'router'
            },
            'time': timestamp,
            'fields': {
                'download_month': int(info['CurrentMonthDownload']),
                'upload_month': int(info['CurrentMonthUpload'])
            }
        },
        {
            'measurement': 'signal',
            'tags': {
                'source': 'router'
            },
            'time': timestamp,
            'fields': {
                'network_type': int(info['EvaluatedNetworkType']),
                'signal_strength': int(info['SignalIcon'])
            }
        }

    ]
    client.write_points(data, time_precision='s')
