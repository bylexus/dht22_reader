#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :

#####
# Creates Temp and Humidity graphs from the RRD databases created with reader.py.
#
# This script needs:
# - python-rrdtool
# - A configuration file (see config.ini.default)
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
from string import Template
from warnings import filterwarnings
import Adafruit_DHT
import rrdtool

config = None
log = None

def getRRDFilename(scopeName):
    datadir = config.get('system','data_dir','data')
    datadir = os.path.dirname(os.path.realpath(__file__)) + '/' + datadir
    return datadir + '/' + scopeName + '.rrd'

def getOutputDir():
    return os.path.dirname(os.path.realpath(__file__)) + '/' + config.get('system','output_dir','output')

def createGraphs(scopeName):
    outdir = getOutputDir()
    graphs = ['12h','24h','5d','7d','1m','6m','1y']
    for graph in graphs:
	temp_graph = outdir + '/' + scopeName + '_temperature_' + graph + '.png'
	hum_graph = outdir + '/' + scopeName + '_humidity_' + graph + '.png'
	
	log.info('Creating graph: Temperature {0}: {1}'.format(graph,temp_graph))
	temp_title = Template(config.get('graph','title_temperature','$set_name')).substitute(set_name = scopeName)
	rrdtool.graph(temp_graph,
  		'-s', '-' + graph,
		'-e', '-1',
		'-t', temp_title,
		'-w', config.get('graph','width','800'),
		'-h', config.get('graph','height','400'),
  		'DEF:temp={0}:temperature:AVERAGE'.format(getRRDFilename(scopeName)),
  		'AREA:temp#0e17b7#0d1677:°C',
		'GPRINT:temp:LAST:Current\:%8.2lf %s',
		'GPRINT:temp:AVERAGE:Average\:%8.2lf %s',
		'GPRINT:temp:MAX:Max.\:%8.2lf %s',
		'GPRINT:temp:MIN:Min.\:%8.2lf %s'
	)

	log.info('Creating graph: Humidity {0}: {1}'.format(graph,temp_graph))
	hum_title = Template(config.get('graph','title_humidity','$set_name')).substitute(set_name = scopeName)
	rrdtool.graph(hum_graph,
  		'-s', '-' + graph,
		'-e', '-1',
		'-t', hum_title,
		'-w', config.get('graph','width','800'),
		'-h', config.get('graph','height','400'),
  		'DEF:hum={0}:humidity:AVERAGE'.format(getRRDFilename(scopeName)),
  		'LINE2:hum#FF0000:Humidity',
		'GPRINT:hum:LAST:Current\:%8.2lf %s',
		'GPRINT:hum:AVERAGE:Average\:%8.2lf %s',
		'GPRINT:hum:MAX:Max.\:%8.2lf %s',
		'GPRINT:hum:MIN:Min.\:%8.2lf %s'
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

scopeName = config.get('dataprovider','set_name')

createGraphs(scopeName)
