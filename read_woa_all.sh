#!/usr/bin/env bash

python read_woa_nc.py \
       --variable "temperature" \
       --resolution "04" \

python read_woa_nc.py \
       --variable "salinity" \
       --resolution "04" \

python read_woa_nc.py \
       --variable "temperature" \
       --resolution "1" \

python read_woa_nc.py \
       --variable "salinity" \
       --resolution "1" \

# At 5 degree there is no objectively analized
python read_woa_nc.py \
       --variable "temperature" \
       --resolution "5" \
       --field "mn" \

python read_woa_nc.py \
       --variable "salinity" \
       --resolution "5" \
       --field "mn" \

