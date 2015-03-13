#!/bin/bash

rrdtool create temptrax.rrd \
	--step 300 \
	DS:probe1-temp:GAUGE:600:55:95 \
	DS:probe2-temp:GAUGE:600:55:95 \
	RRA:MIN:0.5:3:40 \
	RRA:MAX:0.5:3:40 \
	RRA:AVERAGE:0.5:1:40

#rrdtool update temptrax.rrd N:60:90

#rrdtool fetch temptrax.rrd AVERAGE
