#!/usr/bin/env python3

import sys
from your.formats.pysigproc import SigprocFile
from tqdm import tqdm

total_duration_seconds = 0

for fname in tqdm(sys.argv[1:]):
    fil = SigprocFile(fname)
    total_duration_seconds += fil.native_tsamp() * fil.nspectra()

print("Seconds:", total_duration_seconds)
print("Minutes:", total_duration_seconds / 60.)
print("Hours  :", total_duration_seconds / 60. / 60.)
print(f"Hours  : {total_duration_seconds // 3600:.0f}:{(total_duration_seconds % 3600) / 60.:.0f}")
