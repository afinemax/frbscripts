#!/bin/bash
set -e  # Stop on first error

~/frb/get_frb_from_pointing.py  # Check if pointing close to FRB, stop otherwise

screen -dmS filterbank_lband ~/frb/filterbank-lband.sh
screen -dmS filterbank_l2band ~/frb/filterbank-l2band.sh
screen -dmS filterbank_pband ~/frb/filterbank-pband.sh
screen -dmS usrp_lband ~/frb/usrp-lband.sh
sleep 1
screen -dmS usrp_pband ~/frb/usrp-pband.sh
sleep 2
screen -list
echo "Start frb_dashboard.py for a fancy dashboard"
