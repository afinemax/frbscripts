#!/usr/bin/env python3

"""Read results from fetch, move files to subdirectories good and bad"""

import shutil
import os
import pandas as pd

df = pd.read_csv("results_a.csv")

good = df[df['label'] == 1.0]
bad  = df[df['label'] == 0.0]

try:
    os.mkdir("good")
    os.mkdir("bad")
except FileExistsError:
    pass

for fname in good['candidate']:
    try:
        shutil.move(fname, 'good')
        shutil.move(fname.rstrip('.h5') + '.png', 'good')
    except:
        pass
for fname in bad['candidate']:
    try:
        shutil.move(fname, 'bad')
        shutil.move(fname.rstrip('.h5') + '.png', 'bad')
    except:
        pass
