#!/bin/bash
set -e  # Stop on first error

~/frb/get_frb_from_pointing.py  # Check if pointing close to FRB, stop otherwise

if screen -ls | grep usrp_ > /dev/null ; then
    echo "Observations seems to be running already, try stop_frb.sh"
    exit 1
fi

screen -dmS filterbank_l1band ~/frb/filterbank-l1band.sh
screen -dmS filterbank_l2band ~/frb/filterbank-l2band.sh
screen -dmS filterbank_phband ~/frb/filterbank-phband.sh
screen -dmS filterbank_pvband ~/frb/filterbank-pvband.sh
screen -dmS usrp_lband ~/frb/usrp-lband.sh
sleep 1
screen -dmS usrp_pband ~/frb/usrp-pband.sh
sleep 2

~/frb/frb_dashboard.py
