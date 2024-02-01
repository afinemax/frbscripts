#!/usr/bin/env python

from telescope import Telescope
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

dt = Telescope(consoleHost="console")
time.sleep(1.5)

radec = dt.radec

for sourcename, coord in sources.items():
    separation = radec.separation(coord)
    if separation < 0.1 * u.deg:
        print(sourcename)
        sys.exit(0)
sys.exit(1)
