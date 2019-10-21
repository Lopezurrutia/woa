#!/usr/bin/env bash

python read_woa_nc.py \
       --variable "temperature" \
       --resolution "04" \

python read_woa_nc.py \
       --variable "salinity" \
       --resolution "04" \

python read_woa_nc.py \
       --variable "temperature" \
       --resolution "01" \

python read_woa_nc.py \
       --variable "salinity" \
       --resolution "01" \

