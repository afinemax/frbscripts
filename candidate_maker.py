#!/usr/bin/env python

# Based on Candidate.ipynb from your documentation
# Tammo Jan Dijkema, 2024-01-06

import your
from argparse import ArgumentParser
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool

from your.candidate import Candidate
from your.formats.pysigproc import SigprocFile
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

def process_row(args):
    row, filterbankname, image = args
    cand = make_candidate(filterbankname, row["DM"], row["Time (s)"], row["Sigma"])
    fout = cand.save_h5(fnout=make_output_name(filterbankname, cand))
    if image:
        plot_h5(fout, detrend_ft=True, save=True)
        plt.close('all')

def make_output_name(filterbankname, cand):
    base = os.path.basename(filterbankname).rstrip(".fil")
    return f"{base}_tcand_{cand.tcand:.7f}_dm_{cand.dm:.1f}_snr_{cand.snr:.1f}.h5"

def make_candidates_for_singlepulsefile(filterbankname, singlepulsename, sigma=6, time=None, image=False):
    try:
        df = pd.read_fwf(singlepulsename)
    except (pd.errors.EmptyDataError, FileNotFoundError):
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
        pool = Pool(processes=8)
        args_generator = ((row, filterbankname, image) for rownr, row in df.iterrows())
        #for _ in tqdm(pool.imap(process_row, args_generator), total=len(df)):
        for _ in pool.imap(process_row, args_generator):
            pass


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

def time_from_dm(f_mhz, dm):
    """Return time in seconds, to be used in a relative way"""
    return 4149 * dm / f_mhz**2

def get_mjd(mjd1, freq1_mhz, freq2_mhz, dm):
    """Get MJD at freq2_mhz, given detection at mjd1 at freq1_mhz"""
    offset1_s = time_from_dm(freq1_mhz, dm)
    offset2_s = time_from_dm(freq2_mhz, dm)
    return mjd1 + (offset2_s - offset1_s) / (24 * 3600)

def compute_time(filterbankfile, dm, mjd2, f2_mhz):
    fil = SigprocFile(filterbankfile)

    freq_filterbank_mhz = fil.fch1
    mjd_filterbank_start = fil.tstart
    print(freq_filterbank_mhz, mjd_filterbank_start)

    mjd_corrected = get_mjd(mjd2, f2_mhz, freq_filterbank_mhz, dm)
    time_offset = (mjd_corrected - mjd_filterbank_start) * 24 * 3600
    print(f"Computed time = {time_offset} seconds since start")
    print(f"Filterbank duration: {fil.native_tsamp() * fil.nspectra():.1f} seconds")
    if time_offset < 0:
        raise RuntimeError("Computed time before filterbank")
    elif time_offset > fil.native_tsamp() * fil.nspectra():
        raise RuntimeError("Computed time after filterbank")
    return time_offset


if __name__ == "__main__":
    parser = ArgumentParser(description="Create candidates with your from a filterbank. Candidates can be specified manually or take nfrom a singlepulsefile.")
    parser.add_argument("singlepulsefiles", nargs='*')
    parser.add_argument("-f", "--filterbankfile", help="Filterbank file (default: derived from singlepulse file, one directory up)")
    parser.add_argument("-s", "--sigma", help="Sigma (default 6.0)", default=6.0, type=float)
    parser.add_argument("-t", "--time", type=float, help="Use given time (offset from start of file), default: taken from singlepulsefile")
    parser.add_argument("-i", "--image", help="Create PNG files", action='store_true')
    parser.add_argument("-p", "--filterbankpath", help="Filterbank directory")
    parser.add_argument("-dm", "--dm", help="DM (default: taken from singlepulse file)", default=None, type=float)
    parser.add_argument("-f2", help="Frequency in MHz (!) at which the time is specified. Time in filterbank will be shifted based on start time and DM. With this argument, -t is interpreted as mjd", type=float, default=None)
    args = parser.parse_args()

    filterbankfile = args.filterbankfile

    if len(args.singlepulsefiles) == 0 and args.filterbankfile:
        if args.dm is None:
            raise RuntimeError("If no singlepulse-files are given, you need to specify --dm")
        if args.f2:
            time = compute_time(args.filterbankfile, args.dm, args.time, args.f2)
        else:
            time = args.time
        cand = make_candidate(args.filterbankfile, args.dm, time, 0)
        fout = cand.save_h5(fnout=make_output_name(args.filterbankfile, cand))
        if args.image:
            plot_h5(fout, detrend_ft=True, save=True)

    for singlepulsefile in tqdm(args.singlepulsefiles):
        if args.f2 is not None:
            raise RuntimeError("--f2 is not supported for use with a singlepulsefile")
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
