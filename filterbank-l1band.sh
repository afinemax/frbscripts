#!/bin/bash

set -e  # Stop on error

BAND='L1_Band'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/observe_vars.sh"

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
	--num-bins 320 \
	--negative-foff \
	--port 50101 \
	--duration $DURATION

    if [ $? -ne 0 ]; then
        echo "$BAND filterbank $(date -u +'%Y-%m-%dT%H:%M:%S')" >> ~/frb/crashes.txt
    fi
done
