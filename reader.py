#!/usr/bin/env python
#####
# Small helper script to read data from a DHT22 Temperature / Humidity sensor
# and store them into a MySQL db.
#
# This script needs:
# - python-mysqldb
# - The Adafruit Python DHT library: https://github.com/adafruit/Adafruit_Python_DHT
# - A configuration file (see config.ini.default)
#
#
# Wanted features:
# - dynamic ini file via command line (to support multiple configs / sensors)
# - ...
#
# WORK IN PROGRESS
# (c) 2017 Alexander Schenkel, alex@alexi.ch

import os
import sys
import ConfigParser
import logging
import time
import MySQLdb
import random
from warnings import filterwarnings

filterwarnings('ignore', category = MySQLdb.Warning)

class DataProvider:
    @staticmethod
    def getProvider(name, config = None):
        if name == 'randomizer':
            return RandomDataProvider()
        if name == 'dht22':
            return None
        return None

    def readData(self):
        raise Error('Implement in child classes.')

class RandomDataProvider(DataProvider):
    def __init__(self):
        random.seed()

    def readData(self):
        temp = random.random() * 40 - 10 # values from -10 to +30
        hum = random.random() * 100
        return {'temperature': temp, 'humidity': hum}

### reading config file
configFile = os.path.dirname(os.path.realpath(__file__)) + '/reader.ini'
config = ConfigParser.ConfigParser()
config.read(configFile)

### Setup logging facility
log = logging.getLogger('system')
logLevel = config.get('system','log_level')
if logLevel and hasattr(logging,logLevel):
    logLevel = getattr(logging,logLevel)

log.setLevel(logLevel)
# create file handler which logs even debug messages
# fh = logging.FileHandler('spam.log')
# fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logLevel)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
# logger.addHandler(fh)
log.addHandler(ch)

log.info('started')
log.debug('Using config file {0}'.format(configFile))

### setting up DB
db_name = config.get('db','database')
db_host = config.get('db','host')
db_port = int(config.get('db','port'))
db_user = config.get('db','user')
db_pw = config.get('db','password')

log.info('Connecting to {0}@{1}:{2} using user {3}'.format(db_name,db_host,db_port,db_user))

db = None

try:
    db = MySQLdb.connect(host=db_host, port=db_port, db=db_name, user=db_user, passwd=db_pw)

    # creating data table, if needed
    cur = db.cursor()
    cur.execute(
            """
    CREATE TABLE IF NOT EXISTS dht22_data (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        set_name VARCHAR(100),
        measure_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        temperature FLOAT,
        humidity FLOAT
    )
    """)
    cur.close()
except MySQLdb.Error, e:
    log.error('Database error: {0}'.format(str(e)))
    sys.exit(1)


### Setup Data Provider
dp = None
try:
    dp = DataProvider.getProvider(config.get('dataprovider','provider'), config)
    log.debug('Using DataProvider: {0}'.format(dp.__class__.__name__))
except Exception as e:
    log.error('Data Provider error: {0}'.format(str(e)))
    sys.exit(1)


### Fetching and storing data
try:
    data = dp.readData()
    log.debug('Read data: {0}'.format(str(data)))
    set_name = config.get('dataprovider','set_name')
    cur = db.cursor()
    res = cur.execute(
        """
            INSERT INTO dht22_data (set_name,measure_time,temperature,humidity)
            VALUES (%s, NOW(), %s, %s);
        """,
        (set_name,data['temperature'], data['humidity'])
    )
    db.commit()
    cur.close()
except Exception as e:
    log.error('Data Read error: {0}'.format(str(e)))
    sys.exit(1)

db.close()
