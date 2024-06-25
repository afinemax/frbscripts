#!/usr/bin/env python

from astropy.coordinates import SkyCoord
import astropy.units as u
import time
import sys
import os 

# catalog file of sources, located in the same dir as this script
catalog_file = 'frb.cat' # name dm (pc/cm^3) ra (deg) dec (deg)


def load_sources_catalog(filename):
    '''This function reads the frb.cat file and creates a dictionary of SkyCoord objects.'''
    # Get the directory path where the script is located
    script_dir = os.path.dirname(__file__)

    # Create the full path to the local file using os.path.join()
    local_file = os.path.join(script_dir, filename)

    # Check if the file exists
    if not os.path.isfile(local_file):
        raise FileNotFoundError(f"The file {local_file} does not exist.")
    
    sources_catalog = {}
    with open(local_file, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue  # Skip comment lines and empty lines
            parts = line.split()
            name = parts[0]
            ra = float(parts[2])
            dec = float(parts[3])
            sources_catalog[name.upper()] = SkyCoord(ra=ra * u.deg, dec=dec * u.deg)
    
    return sources_catalog

# Load the sources catalog from the file
sources = load_sources_catalog('frb.cat')

use_telescope = False

if use_telescope:
    from telescope import Telescope
    dt = Telescope(consoleHost="console")
    time.sleep(1.2)

    pointing = dt.radec
else:
    from vrtzmq import VRTSubscriber
    try:
        subscriber = VRTSubscriber("console", 50011)
        metadata = subscriber.get_dt_metadata()
    except TimeoutError:
        print("Cannot get pointing from console!", file=sys.stderr)
        sys.exit(1)
    ra = metadata['current_pointing_right_ascension'] * u.rad
    dec = metadata['current_pointing_declination'] * u.rad
    pointing = SkyCoord(ra=ra, dec=dec)

for sourcename, coord in sources.items():
    separation = pointing.separation(coord)
    if separation < 0.1 * u.deg:
        print(sourcename)
        sys.exit(0)
print("Not pointed at an FRB!", file=sys.stderr)
sys.exit(1)
