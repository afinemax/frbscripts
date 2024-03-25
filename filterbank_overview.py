#!/usr/bin/env python

from filterbank_duration import filterbank_duration
from glob import glob
import sys
import os

def format_hours(seconds):
    return f"{seconds // 3600:.0f}:{(seconds % 3600) // 60.:02.0f}"

if len(sys.argv) == 1:
    folders_to_search = []
    for mount in ["/home/cephfs/camrasdemo/frb/", "/media/camrasdemo/frbdata/"]:
        date_dirs = sorted(glob(f"{mount}/2024*"))
        folders_to_search += date_dirs
else:
    folders_to_search = sys.argv[1:]

for folder in folders_to_search:
    for band in ["L_", "L1_", "L2_", "P_", "PH", "PV"]:
        for source in ["PSRB0329", "FRB20220912A", "FRB20240114A", "CRAB", "FRB20201124A"]:
            pattern = f"{folder}/{source}*{band}*fil"
            file_list = sorted(glob(pattern))
            duration_seconds = filterbank_duration(file_list, quiet=True)
            mount = os.path.abspath(folder).split("/")[1]
            if duration_seconds > 0:
                print(mount, folder.split("/")[-1], band, source, format_hours(duration_seconds), f"{duration_seconds/3600:.1f}", sep=",")
