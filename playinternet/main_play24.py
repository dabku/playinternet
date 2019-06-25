from scrapers.play24 import Play24
from helpers import set_logger
from influxdb import InfluxDBClient
from time import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import traceback
import sys
import os
import logging

import json

logger = logging.getLogger()


def send_to_db(usage, timestamp, db_config):
    logger.debug('Saving data to database')
    client = InfluxDBClient(db_config['host'], db_config['port'], db_config['user'], db_config['password'],
                            db_config['db_name'])

    data = [{
        'measurement': 'dataUsage',
        'tags': {
            'source': 'play24'
        },
        'time': timestamp,
        'fields': {
            'total_month': usage
        }
    }]

    client.write_points(data, time_precision='s')
    client.close()
    logger.debug('Data saved!')


def create_webdriver(scraper_config):
    if scraper_config['remote']:
        driver = webdriver.Remote(scraper_config['remote'], DesiredCapabilities.CHROME)
    else:
        os.environ['DISPLAY'] = ':99'
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--no-gpu")
        driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_page_load_timeout(scraper_config['timeout'])
    return driver


def get_usage_from_play24(scraper_config):
    timestamp = int(time())
    driver = create_webdriver(scraper_config)
    p24 = Play24(login=scraper_config['play24']['login'], password=scraper_config['play24']['password'],
                 selenium_driver=driver)
    try:
        usage, unit = p24.scrape_current_month_usage().split()
    except AttributeError:
        logger.error('Data in unknown format')
        return
    except Exception as e:
        _exc_type, _exc_value, _exc_traceback = sys.exc_info()
        logger.error(traceback.format_exception(_exc_type, _exc_value, _exc_traceback))
        return
    finally:
        driver.quit()

    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
        'TB': 1024 * 1024 * 1024 * 1024
    }

    usage = int(float(usage.replace(',', '.')) * units[unit])
    return {
        'usage': usage,
        'timestamp': timestamp
    }


if __name__ == '__main__':

    with open('config_play24.json', 'r') as f:
        config = json.load(f)

    set_logger(logger, filename=config['logger']['file_name'], level=config['logger']['level'])

    logger.debug('Started Play24 Scraper')
    data_dict = {}
    tries = 0
    while not data_dict:
        tries += 1
        logger.info('Getting data... Try: {}'.format(tries))
        data_dict = get_usage_from_play24(config['scraper'])
    logger.debug(data_dict)
    try:
        send_to_db(data_dict['usage'], data_dict['timestamp'], config['db'])
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
