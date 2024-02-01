#!/bin/bash

#trap "exit" INT TERM ERR
#trap "kill 0" EXIT

while true
do

  ~camrasdemo/thomas/vrt-iq-tools/usrp_to_vrt --rate 100e6 \
	--freq 1250e6,1350e6 \
	--gain 70 \
	--continue \
	--usrp-channel 0,1\
	--int-second \
	--ref external \
	--merge-address console \
	--port 50101 \
	--arg "recv_buff_size=20000000,serial=313BCE6,num_recv_frames=2048" \
	--progress \
	--ant RX1,RX1

done
