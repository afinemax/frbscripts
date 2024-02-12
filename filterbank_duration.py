#!/usr/bin/env python3

import sys
from your.formats.pysigproc import SigprocFile
from tqdm import tqdm
from argparse import ArgumentParser

def filterbank_duration(file_list, quiet=False):
    total_duration_seconds = 0

    for fname in tqdm(file_list, disable=quiet):
        fil = SigprocFile(fname)
        total_duration_seconds += fil.native_tsamp() * fil.nspectra()

    return total_duration_seconds

if __name__ == "__main__":
    parser = ArgumentParser("Show duration of filterbank files")
    parser.add_argument("files", nargs='+')

    args = parser.parse_args()

    total_duration_seconds = filterbank_duration(args.files)

    print(f"Hours  : {total_duration_seconds // 3600:.0f}:{(total_duration_seconds % 3600) // 60.:02.0f}")
