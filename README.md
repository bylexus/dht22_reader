DHT22 Temperature and Humidity reader utility
=============================================

This small set of utitlities is a collection of tools for my private project to collect temperature and humidity data, using a DHT22 sensor and a Raspberry PI.
It contains (for now) two utilities:

reader.py
---------

Reads Temperature and Humidity data from a DHT22 sensor and stores the data into a RRD database.
Execute this script everny 5 minutes via crontab, e.g. like this:

```
$ crontab -e
# CRONTAB 
*/5 *   *   *   *    /usr/bin/env python /path/to/dht22_reader/reader.py
```

Make sure to edit `reader.ini`

create_graphs.py
----------------

Creates graphs from the RRD database. Execute when updates are needed.

Make sure to edit `reader.ini`

Config
--------

All config is done in `reader.ini`. Please have a look at the example at `reader.init.default`.
In a future version, the command line python utils will support multiple configs, for now it is hard-coded.

Requirements
------------

* A Raspberry PI
* A DHT22 Sensor
* python >= 2.4
* python-rrdtool
* The Adafruit Python DHT library: https://github.com/adafruit/Adafruit_Python_DHT
* Some time for making, soldering, tinkering



(c) 2017 Alexander Schenkel, alexi.ch
