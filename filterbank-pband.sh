#!/bin/bash

#trap "exit" INT TERM ERR
#trap "kill 0" EXIT
set -e  # Stop on error

#DATADIR='/data2/camrasdemo/frb'
DATADIR='/data/camrasdemo/frb'
#DATADIR='/home/cephfs/camrasdemo/frb/live'

#OBJECT="CRAB"
#OBJECT='FRB20220912A'
#OBJECT='FRB20201124A'
#OBJECT='PSRJ1809-1943'
#OBJECT='FRB20240114A'
OBJECT=$(~/frb/get_frb_from_pointing.py)

BAND='P_Band'
DURATION=600

while true
do

  NOW=`date +"%Y_%m_%d_%H_%M_%S"`
  FILENAME=$OBJECT"_"$BAND"_"$NOW.fil

  echo $FILENAME

  ~camrasdemo/thomas/vrt-iq-tools/vrt_to_filterbank \
	--file $DATADIR/$FILENAME \
	--source-name $OBJECT \
	--dt-trace \
	--int-second \
	--telescope-id 8 \
	--integration-time 0.0002 \
	--num-bins 160 \
	--negative-foff \
	--port 50100 \
	--duration $DURATION

    if [ $? -ne 0 ]; then
        echo "$BAND filterbank $(date -u +'%Y-%m-%dT%H:%M:%S')" >> ~/frb/crashes.txt
    fi
done
