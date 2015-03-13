import sys
#sys.path.append('/path/to/rrdtool/lib/python2.3/site-packages/')
import rrdtool, tempfile

DAY = 86400
YEAR = 365 * DAY
fd,path = tempfile.mkstemp('.png')

rrdtool.graph(path,
              '--imgformat', 'PNG',
              '--width', '540',
              '--height', '100',
              '--start', "-%i" % YEAR,
              '--end', "-1",
              '--vertical-label', 'Downloads/Day',
              '--title', 'Annual downloads',
              '--lower-limit', '0',
              'DEF:downloads=downloads.rrd:downloads:AVERAGE',
              'AREA:downloads#990033:Downloads')

info = rrdtool.info('downloads.rrd')

print info['last_update']
print info['ds']['downloads']['minimal_heartbeat']

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
