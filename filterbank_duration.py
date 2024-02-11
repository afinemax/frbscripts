#!/usr/bin/env python3

import sys
from your.formats.pysigproc import SigprocFile
from tqdm import tqdm
from argparse import ArgumentParser

def main(file_list):
    total_duration_seconds = 0

    for fname in tqdm(sys.argv[1:]):
        fil = SigprocFile(fname)
        total_duration_seconds += fil.native_tsamp() * fil.nspectra()

    print(f"Hours  : {total_duration_seconds // 3600:.0f}:{(total_duration_seconds % 3600) / 60.:02.0f}")

if __name__ == "__main__":
    parser = ArgumentParser("Show duration of filterbank files")
    parser.add_argument("files", nargs='+')

    args = parser.parse_args()

    main(args.files)
