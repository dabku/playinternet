from time import sleep, time
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError
from pythonping import ping
from helpers import set_logger
import json
from collections import deque
import traceback
import sys
import logging
from os import path

logger = logging.getLogger()

if __name__ == '__main__':

    script_dir = path.dirname(path.realpath(sys.argv[0]))
    with open(path.join(script_dir,'config_ping.json'), 'r') as f:
        config = json.load(f)

    set_logger(logger, filename=config['logger']['file_name'], level=config['logger']['level'])
    logger.info('Started')

    client = InfluxDBClient(config['db']['host'], config['db']['port'], config['db']['user'], config['db']['password'],
                            config['db']['db_name'])
    data_q = deque(maxlen=1024)
    while True:
        response_list = ping(config['ping']['host'], count=config['ping']['count'])
        timestamp = int(time())
        logger.debug("Got {}ms max, {}ms min, {}ms avg".format(response_list.rtt_max_ms, response_list.rtt_min_ms,
                                                               response_list.rtt_avg_ms))

        data = [
            {
                'measurement': 'ping',
                'tags': {
                    'destination': config['ping']['host']
                },
                'time': timestamp,
                'fields': {
                    'max': response_list.rtt_max_ms,
                    'min': response_list.rtt_min_ms,
                    'avg': response_list.rtt_avg_ms
                }
            }
        ]
        data_q.append(data)
        while data_q:
            item = data_q.pop()
            try:
                client.write_points(item, time_precision='s')
            except InfluxDBServerError:
                logging.error('Failed to save data to the database')
                data_q.append(item)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(traceback.format_exception(exc_type, exc_value, exc_traceback))
                break
        sleep(config['ping']['sleep'])
