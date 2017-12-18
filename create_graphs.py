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

def toBool(s):
    return str(s).lower() in ['yes','true','1','ok','on','ja','yup','yarr','y']

def getRRDFilename(scopeName):
    datadir = config.get('system','data_dir')
    datadir = os.path.dirname(os.path.realpath(__file__)) + '/' + datadir
    return datadir + '/' + scopeName + '.rrd'

def getOutputDir():
    return os.path.dirname(os.path.realpath(__file__)) + '/' + config.get('system','output_dir')

def createGraphs(scopeName):
    outdir = getOutputDir()
    graphs = ['12 hours','24 hours','5 days','7 days','1 months','6 months','1 years']
    lower_limit = config.get('graph','lower_limit') if config.has_option('graph','lower_limit') else '0'
    enable_combined = toBool(config.get('graph','enable_combined')) if config.has_option('graph','enable_combined') else True
    enable_temp_graph = toBool(config.get('graph','enable_temp_graph')) if config.has_option('graph','enable_temp_graph') else True
    enable_humidity_graph = toBool(config.get('graph','enable_humidity_graph')) if config.has_option('graph','enable_humidity_graph') else True
    for graph in graphs:
        if enable_combined:
            title = Template(config.get('graph','title','$set_name')).substitute(set_name = scopeName)
            graph_file = outdir + '/' + scopeName + '_combined_' + graph.replace(' ','_') + '.png'

            log.info('Creating graph: {0}: {1}'.format(graph,graph_file))
            rrdtool.graph(graph_file,
                    '-s', '-' + graph,
                    '-e', '-1',
                    '-t', title,
                    '--lower-limit',lower_limit,
                    '-w', config.get('graph','width'),
                    '-h', config.get('graph','height'),
                    'DEF:humidity={0}:humidity:AVERAGE'.format(getRRDFilename(scopeName)),
                    'VDEF:hum_avg=humidity,AVERAGE',
                    'AREA:humidity#9dcbf9#306aa5:Hum.(%)  ',
                    'GPRINT:humidity:LAST:Current\:%8.2lf %s',
                    'GPRINT:humidity:MAX:Max.\:%8.2lf %s',
                    'GPRINT:humidity:MIN:Min.\:%8.2lf %s\\n',
                    'LINE2:hum_avg#00FF00:Average Humidity\\:',
                    'GPRINT:humidity:AVERAGE:%8.2lf %s\\n',
                    'DEF:temperature={0}:temperature:AVERAGE'.format(getRRDFilename(scopeName)),
                    'VDEF:temp_avg=temperature,AVERAGE',
                    'LINE3:temperature#FF0000:Temp.(°C)',
                    'GPRINT:temperature:LAST:Current\:%8.2lf %s',
                    'GPRINT:temperature:MAX:Max.\:%8.2lf %s',
                    'GPRINT:temperature:MIN:Min.\:%8.2lf %s\\n',
                    'LINE1:temp_avg#aa0000:Average Temperature\\:',
                    'GPRINT:temperature:AVERAGE:%8.2lf %s\\n',
            )

        # separate graphs:
        if enable_temp_graph:
            temp_graph = outdir + '/' + scopeName + '_temperature_' + graph + '.png'

            log.info('Creating graph: Temperature {0}: {1}'.format(graph,temp_graph))
            temp_title = Template(config.get('graph','title_temperature')).substitute(set_name = scopeName)
            rrdtool.graph(temp_graph,
                    '-s', '-' + graph,
                    '-e', '-1',
                    '-t', temp_title,
                    '--lower-limit',lower_limit,
                    '-w', config.get('graph','width'),
                    '-h', config.get('graph','height'),
                    'DEF:temp={0}:temperature:AVERAGE'.format(getRRDFilename(scopeName)),
                    'VDEF:temp_avg=temp,AVERAGE',
                    'LINE3:temp#FF0000:Temp.(°C)',
                    'GPRINT:temp:LAST:Current\:%8.2lf %s',
                    'GPRINT:temp:MAX:Max.\:%8.2lf %s',
                    'GPRINT:temp:MIN:Min.\:%8.2lf %s\\n',
                    'LINE1:temp_avg#aa0000:Average Temperature\\:',
                    'GPRINT:temp:AVERAGE:%8.2lf %s\\n'
            )

        if enable_humidity_graph:
            hum_graph = outdir + '/' + scopeName + '_humidity_' + graph + '.png'
            log.info('Creating graph: Humidity {0}: {1}'.format(graph,hum_graph))
            hum_title = Template(config.get('graph','title_humidity')).substitute(set_name = scopeName)
            rrdtool.graph(hum_graph,
                    '-s', '-' + graph,
                    '-e', '-1',
                    '-t', hum_title,
                    '--lower-limit',lower_limit,
                    '-w', config.get('graph','width'),
                    '-h', config.get('graph','height'),
                    'DEF:hum={0}:humidity:AVERAGE'.format(getRRDFilename(scopeName)),
                    'VDEF:hum_avg=hum,AVERAGE',
                    'AREA:hum#9dcbf9#306aa5:Hum.(%)  ',
                    'GPRINT:hum:LAST:Current\:%8.2lf %s',
                    'GPRINT:hum:MAX:Max.\:%8.2lf %s',
                    'GPRINT:hum:MIN:Min.\:%8.2lf %s\\n',
                    'LINE2:hum_avg#00FF00:Average Humidity\\:',
                    'GPRINT:hum:AVERAGE:Average\:%8.2lf %s\\n'
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
