#!/usr/bin/env python3

import os

import numpy as np
import your
from your import Writer, Your
from your.candidate import Candidate
from your.formats.filwriter import make_sigproc_object
from your.utils.plotter import plot_h5, save_bandpass

from tqdm import tqdm


def combine_bands(fil_file1, fil_file2):
    """
    Combine two filterbank files, fil_file1 should be L1 (1400-1300), fil_file2 should be L2 (1300-1200)
    """
    chunksize = 100000

    assert "L_Band" in fil_file1 or "L1_Band" in fil_file1
    assert "L2_Band" in fil_file2

    your1 = your.Your(fil_file1)
    l1_mean = your1.get_data(nstart=0, nsamp=chunksize).mean()

    your2 = your.Your(fil_file2)
    l2_mean = your2.get_data(nstart=0, nsamp=chunksize).mean()

    output_fil = fil_file1.replace("L1", "L12")
    assert output_fil != fil_file1

    sigproc_object = make_sigproc_object(
        rawdatafile=output_fil.rstrip(".fil"),
        source_name=your1.your_header.source_name,
        nchans=640,
        foff=your1.your_header.foff,
        fch1=1400,  # MHz
        tsamp=your1.your_header.tsamp,
        tstart=your1.your_header.tstart,
        #    src_raj= your_object.your_header.src_raj,
        #    src_dej= your_object.your_header.src_dej,
        machine_id=5,
        nbeams=1,
        ibeam=1,
        nbits=32,
        nifs=1,
        barycentric=0,
        pulsarcentric=0,
        telescope_id=8,
        data_type=0,
        az_start=-1,
        za_start=-1,
    )

    sigproc_object.write_header(output_fil)

    nspectra = your1.your_header.nspectra

    assert your1.your_header.nspectra == your2.your_header.nspectra

    for nstart in tqdm(range(0, nspectra, chunksize)):
        nsamp = min(chunksize, nspectra - nstart)
        data1 = your1.get_data(nstart=nstart, nsamp=nsamp)
        data2 = your1.get_data(nstart=nstart, nsamp=nsamp)
        data12 = np.hstack([data2 / l2_mean, data1 / l1_mean])
        sigproc_object.append_spectra(data12, output_fil)


if __name__ == "__main__":
    #fil_file1 = "CRAB_L1_Band_2024_02_08_18_40_15.fil"
    #fil_file2 = "CRAB_L2_Band_2024_02_08_18_40_15.fil"

    fil_file1, fil_file2 = sys.argv[1], sys.argv[2]

    main(fil_file1, fil_file2)
