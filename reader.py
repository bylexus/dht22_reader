#!/usr/bin/env python
#####
# Small helper script to read data from a DHT22 Temperature / Humidity sensor
# and store them in a RRD database using python's rrdtool bindings
#
# This script needs:
# - python-rrdtool
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
import random
from warnings import filterwarnings
import Adafruit_DHT
import rrdtool

config = None

class DataProvider:
    @staticmethod
    def getProvider(name, config = None):
        if name == 'randomizer':
            return RandomDataProvider(config)
        if name == 'dht22':
            return DHT22DataProvider(config)
        return None

    def readData(self):
        raise Error('Implement in child classes.')

class RandomDataProvider(DataProvider):
    def __init__(self, config):
        random.seed()

    def readData(self):
        temp = random.random() * 40 - 10 # values from -10 to +30
        hum = random.random() * 100
        return {'temperature': temp, 'humidity': hum}

class DHT22DataProvider(DataProvider):
    def __init__(self, config):
        self.pin = int(config.get('dataprovider','gpio'))

    def readData(self):
        humidity = None
        temperature = None
        while humidity is None or temperature is None:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
        return {'temperature':temperature, 'humidity': humidity}

def getRRDFilename(scopeName):
    datadir = config.get('system','data_dir','data')
    datadir = os.path.dirname(os.path.realpath(__file__)) + '/' + datadir
    return datadir + '/' + scopeName + '.rrd'

def createRRD(scopeName, measure_inverval,log):
    rrdFile = getRRDFilename(scopeName)
    if not os.path.isfile(rrdFile):
        log.info('Creating RRD DB File: {0}'.format(rrdFile))
        rrdtool.create( rrdFile,
                  '--step', str( measure_interval ),
                  '--no-overwrite',
                  'DS:temperature:GAUGE:'+str(measure_interval*2)+':-273:5000',
                  'DS:humidity:GAUGE:'+str(measure_interval*2)+':0:100',
                  'RRA:AVERAGE:0.5:1:576',
                  'RRA:AVERAGE:0.5:48:168',
                  'RRA:AVERAGE:0.5:288:1825',
                  'RRA:AVERAGE:0.5:8640:600'
        )
    return rrdFile

def updateRRD(scopeName, data, log):
    rrdFile = getRRDFilename(scopeName)
    temp = str(data['temperature'])
    hum = str(data['humidity'])
    log.debug('Updating RRD {0} with Temp: {1}, Humidity: {2}'.format(rrdFile, temp, hum))
    rrdtool.update(rrdFile,
            '-t','temperature:humidity',
            'N:{0}:{1}'.format(temp,hum)
    )

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

### Setup Data Provider
dp = None
try:
    dp = DataProvider.getProvider(config.get('dataprovider','provider'), config)
    log.debug('Using DataProvider: {0}'.format(dp.__class__.__name__))
except Exception as e:
    log.error('Data Provider error: {0}'.format(str(e)))
    sys.exit(1)


### create RRD file
set_name = config.get('dataprovider','set_name')
measure_interval = int(config.get('dataprovider','measure_interval',300))
rrdFile = createRRD(set_name, measure_interval, log)

### Fetching and storing data
try:
    data = dp.readData()
    log.debug('Read data: {0}'.format(str(data)))

    ### store into RRD:
    updateRRD(set_name, data, log)
except Exception as e:
    log.error('Data Read error: {0}'.format(str(e)))
    sys.exit(1)

