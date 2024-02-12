#!/usr/bin/env python

from filterbank_duration import filterbank_duration
from glob import glob

def format_hours(seconds):
    return f"{seconds // 3600:.0f}:{(seconds % 3600) // 60.:02.0f}"

for mount in ["/home/cephfs/camrasdemo/frb/", "/media/camrasdemo/frbdata/"]:
    for band in ["L_", "L1_", "L2_", "P_"]:
        for source in ["PSRB039", "FRB20220912A", "FRB20240114A", "CRAB", "FRB20201124A"]:
            date_dirs = sorted(glob(f"{mount}/2024*"))
            for date_dir in date_dirs:
                pattern = f"{date_dir}/{source}*{band}*fil"
                file_list = sorted(glob(pattern))
                duration_seconds = filterbank_duration(file_list, quiet=True)
                if duration_seconds > 0:
                    print(mount, date_dir.split("/")[-1], band, source, format_hours(duration_seconds), sep=",")
