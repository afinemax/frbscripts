#!/usr/bin/env python

from astropy.coordinates import SkyCoord
import astropy.units as u
import time
import sys

sources = {
        'CRAB': SkyCoord(ra=83.63*u.deg, dec=22.01*u.deg),
        'FRB20220912A': SkyCoord(ra=347.27*u.deg, dec=48.71*u.deg),
        'FRB20201124A': SkyCoord(ra=77.01*u.deg, dec=26.06*u.deg),
        'FRB20240114A': SkyCoord(ra=321.92*u.deg, dec=4.35*u.deg)
        }

use_telescope = False

if use_telescope:
    from telescope import Telescope
    dt = Telescope(consoleHost="console")
    time.sleep(1.2)

    pointing = dt.radec
else:
    from vrtzmq import VRTSubscriber
    subscriber = VRTSubscriber("console", 50011)
    metadata = subscriber.get_dt_metadata()
    ra = metadata['current_pointing_right_ascension'] * u.rad
    dec = metadata['current_pointing_declination'] * u.rad
    pointing = SkyCoord(ra=ra, dec=dec)

for sourcename, coord in sources.items():
    separation = pointing.separation(coord)
    if separation < 0.1 * u.deg:
        print(sourcename)
        sys.exit(0)
print("Not pointed at an FRB!")
sys.exit(1)
