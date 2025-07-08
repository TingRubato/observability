#!/bin/bash

# Set up environment for cron
export PATH="/home/ting@domain.bhs1.com/miniforge3/bin:$PATH"
export CONDA_DEFAULT_ENV="base"

for machine in mazak_1_vtc_200 mazak_2_vtc_300 mazak_3_350msy mazak_4_vtc_300c; do 
    for endpoint in current sample; do
        echo "Processing $machine - $endpoint"
        case $machine in 
            mazak_1_vtc_200) machine_num=1 ;; 
            mazak_2_vtc_300) machine_num=2 ;; 
            mazak_3_350msy) machine_num=3 ;; 
            mazak_4_vtc_300c) machine_num=4 ;; 
        esac
        case $endpoint in 
            current) endpoint_num=1 ;; 
            sample) endpoint_num=2 ;; 
        esac
        echo -e "$machine_num\n$endpoint_num" | /home/ting@domain.bhs1.com/miniforge3/bin/python src/scripts/xml2json_deduplicated.py
    done
done
