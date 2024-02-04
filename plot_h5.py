#!/usr/bin/env python

from your.utils.plotter import plot_h5
import sys
from tqdm import tqdm
import matplotlib.pyplot as plt

for h5file in tqdm(sys.argv[1:]):
    plot_h5(h5file, detrend_ft=False, save=True)
    plt.close('all')
