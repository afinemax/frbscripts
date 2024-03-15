#!/bin/bash

#trap "exit" INT TERM ERR
#trap "kill 0" EXIT

while true
do

  ~camrasdemo/thomas/vrt-iq-tools/usrp_to_vrt --rate 20e6 \
	--freq 410e6 \
	--gain 30 \
	--usrp-channel 0 \
	--int-second \
	--ref external \
	--merge-address console \
	--port 50100 \
	--arg "serial=30F7D7D" \
	--ant RX2 \
	--progress

  echo "P-band" USRP $(date -u +"%Y-%m-%dT%H:%M:%S") >> ~/frb/crashes.txt
done
