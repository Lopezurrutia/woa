# Project Title

Reads WORLD OCEAN ATLAS 2018 (WOA18) variables and creates python numpy matrix with climatologies.

## Getting Started
See https://www.nodc.noaa.gov/OC5/woa18/ for information on the World Ocean Atlas variables, resolution, etc.
Download all variables and resolutions by running the bash script:
'''
./read_woa_all.sh
'''

The compressed numpy files are saved to the output dir (default to woa_np), one file per variable.
The resulting files are provided in the git repository using git lfs


## Other files not used
- read_woa_csv.py:  Reads the woa data from csv file format
- read_woa_iris.py: Uses iris and python-oceans packages to extract data from coordinates

## Prerequisites

NetCDF4 python library, there is also an (unmaintained) read_woa_csv.py file where you can get ideas on how to read the data from csv files, without the need of NetCDF

## Authors
[Angel Lopez-Urrutia](https://lopezurrutia.github.com/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
 woa url formatting from [python-oceans](https://github.com/ocefpaf/python-oceans)

