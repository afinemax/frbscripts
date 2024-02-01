#!/bin/bash

screen -dmS filterbank_lband ./filterbank-lband.sh
screen -dmS filterbank_l2band ./filterbank-l2band.sh
screen -dmS filterbank_pband ./filterbank-pband.sh
screen -dmS usrp_lband ./usrp-lband.sh
screen -dmS usrp_pband ./usrp-pband.sh
