#!/usr/bin/env python

from datetime import datetime, timedelta, date

start = datetime.now()

det_is_OK = False

# Here we try a fraction  
detString = '/2'
try:
    (numerator, denominator) = detString.split('/')
    fraction = float(numerator)/float(denominator)
    det_is_OK = True
except ValueError as e:
    print 'fck ', e
    fraction = None

print fraction
print det_is_OK

end = datetime.now()

# A timedelta is actually a tuple of days, seconds and microseconds.
d = end-start
print d.seconds

optdet = None
if optdet<0 or optdet>1:
    print 'XX', optdet
else:
    print 'OK', optdet



