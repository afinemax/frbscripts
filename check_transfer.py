#!/usr/bin/env python3

from tqdm import tqdm
from subprocess import check_output
import time


def get_size():
    res = check_output("du -bc /media/camrasdemo/frbdata/2024-03-19/", shell=True)
    size = int(res.splitlines()[-1].split()[0])
    return size

def main():
    size = get_size()
    with tqdm(unit='B', initial=get_size(), unit_scale=True, desc='Size', total=349*1024**3) as pbar:
        while size > 100:
            size = get_size()
            pbar.update(size - pbar.n)
            time.sleep(1)


if __name__ == "__main__":
    main()
