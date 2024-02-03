#!/bin/bash
set -e  # Stop on first error

~/frb/get_frb_from_pointing.py  # Check if pointing close to FRB, stop otherwise

screen -dmS filterbank_lband ./filterbank-lband.sh
screen -dmS filterbank_l2band ./filterbank-l2band.sh
screen -dmS filterbank_pband ./filterbank-pband.sh
screen -dmS usrp_lband ./usrp-lband.sh
sleep 1
screen -dmS usrp_pband ./usrp-pband.sh
