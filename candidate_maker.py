#!/usr/bin/env python

# Based on Candidate.ipynb from your documentation
# Tammo Jan Dijkema, 2024-01-06

import your
from argparse import ArgumentParser
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from your.candidate import Candidate
from your.utils.plotter import plot_h5
import logging
import numpy as np
from scipy.signal import detrend
import os
import re

plt.set_loglevel("error")

os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s -" " %(message)s",
)

def make_output_name(filterbankname, cand):
    base = os.path.basename(filterbankname).rstrip(".fil")
    return f"{base}_tcand_{cand.tcand:.7f}_dm_{cand.dm:.1f}_snr_{cand.snr:.1f}.h5"

def make_candidates_for_singlepulsefile(filterbankname, singlepulsename, sigma=6, time=None, image=False):
    try:
        df = pd.read_fwf(singlepulsename)
    except pd.errors.EmptyDataError:
        return

    if "# DM" in df.columns:
        df = df.rename(columns={"# DM": "DM"})
    df = df[df["Sigma"] > sigma]

    if time is not None:
        dm = df.iloc[0]["DM"]  # Assumes all DM are equal, which should be the case in a singlepulse file
        cand = make_candidate(filterbankname, dm, time, 10)  # Dummy sigma
        fout = cand.save_h5(fnout=make_output_name(filterbankname, cand))
        if (image):
            plot_h5(fout, detrend_ft=True, save=True)
            plt.close('all')
    else:
        for rownr, row in tqdm(df.iterrows(), total=len(df), leave=False):
            cand = make_candidate(filterbankname, row["DM"], row["Time (s)"], row["Sigma"])
            fout = cand.save_h5(fnout=make_output_name(filterbankname, cand))
            if (image):
                plot_h5(fout, detrend_ft=True, save=True)
                plt.close('all')


def make_candidate(filterbankname, dm, tcand, sigma):
    cand = Candidate(
        fp=filterbankname,
        dm=dm,
        tcand=tcand,
        width=2,
        label=-1,
        snr=sigma,
        min_samp=256,
        device=0,
    )
    cand.get_chunk()
    cand.dmtime()
    cand.dedisperse()
    cand.dm_opt, cand.snr_opt = cand.optimize_dm()
    cand.resize(key="ft", size=256, axis=0, anti_aliasing=True)  # Resize along time axis
    cand.resize(key="ft", size=256, axis=1, anti_aliasing=True)  # Resize along frequency axis
    cand.resize(key="dmt", size=256, axis=1, anti_aliasing=True)

    return cand


if __name__ == "__main__":
    parser = ArgumentParser(description="Parse singlepulse file, run 'your' candidate processing on high sigma detections, save h5 and png")
    parser.add_argument("singlepulsefiles", nargs='+')
    parser.add_argument("-f", "--filterbankfile", help="Filterbank file (default: derived from singlepulse file, one directory up)")
    parser.add_argument("-s", "--sigma", help="Sigma (default 6.0)", default=6.0, type=float)
    parser.add_argument("-t", "--time", type=float, help="Do not look in the singlepulse file (just use its DM)")
    parser.add_argument("-i", "--image", help="Create PNG files", action='store_true')
    parser.add_argument("-p", "--filterbankpath", help="Filterbank directory")
    args = parser.parse_args()

    filterbankfile = args.filterbankfile

    for singlepulsefile in tqdm(args.singlepulsefiles):
        if args.filterbankfile is None:
            # FRB20220912A_435_snip_DM222.00.singlepulse
            filterbankfile = re.sub(r'_DM([\d.]+).singlepulse$', '.fil', singlepulsefile)
            if filterbankfile == singlepulsefile:
                raise RuntimeError("Cannot guess filterbank filename from " + singlepulsefile)
            singlepulsedir = os.path.dirname(singlepulsefile)
            if args.filterbankpath:
                filterbankdirectory = args.filterbankpath
            else:
                filterbankdirectory = os.path.join(singlepulsedir, '..')
            filterbankfile = os.path.abspath(os.path.join(filterbankdirectory, filterbankfile))
        else:
            filterbankfile = args.filterbankfile
    
        make_candidates_for_singlepulsefile(filterbankfile, singlepulsefile, args.sigma, args.time, args.image)
