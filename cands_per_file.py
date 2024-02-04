#!/usr/bin/env python

import sys
import os
cands_per_file = {}


for candname in sys.argv[1:]:
    filterbankname = os.path.basename(candname[:candname.index("_tcand")] + ".fil")
    cands_per_file[filterbankname] = cands_per_file.get(filterbankname, 0) + 1

for filterbankname, num_cands in cands_per_file.items():
    print(filterbankname, num_cands, sep='\t')
