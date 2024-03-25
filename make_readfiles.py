#!/usr/bin/env python3

import subprocess
from glob import glob
from os.path import basename
from tqdm import tqdm

readfilepath = "/home_local/camrasdemo/psrsoft/usr/bin/readfile"

for filterbankfile in tqdm(sorted(glob("*.fil"))):
    outputname = "/media/camrasdemo/frbdata/headers2/" + basename(filterbankfile).replace(".fil", ".txt")
    with open(outputname, "w") as outputfile:
        output = subprocess.call([readfilepath, filterbankfile], stdout=outputfile)
