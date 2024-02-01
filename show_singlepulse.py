#!/usr/bin/env python3

import pandas as pd
from glob import glob
from argparse import ArgumentParser
import numpy as np

def main(singlepulsefiles, time=None):
    if singlepulsefiles is None:
        singlepulsefiles = glob("*.singlepulse")

    if len(singlepulsefiles) == 0:
        raise RuntimeError("No singlepulsefiles found")
    
    df = None
    for singlepulsefile in singlepulsefiles:
        if df is None:
            try:
                df = pd.read_fwf(singlepulsefile)
                df["Filename"] = singlepulsefile
            except pd.errors.EmptyDataError:
                pass
        else:
            try:
                df1 = pd.read_fwf(singlepulsefile)
                df1["Filename"] = singlepulsefile
            except pd.errors.EmptyDataError:
                continue
            df = pd.concat([df, df1])

    if df is None:
        raise RuntimeError("All data files empty!")

    if time is not None:
        df = df[np.abs(time - df["Time (s)"]) < 5]

    print(df.sort_values("Sigma", ascending=False))

if __name__ == "__main__":
    parser = ArgumentParser("Inspect singlepulsefiles")
    parser.add_argument("singlepulsefiles", nargs='*')
    parser.add_argument("--time", "-t", help="Time to search around", type=float)
    args = parser.parse_args()
    main(args.singlepulsefiles, args.time)
