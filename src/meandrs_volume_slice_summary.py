#!/usr/bin/env python
# ******************************************************************************
# meandrs_volume_slice_summary.py
# ******************************************************************************
# Purpose:
# Aggregate regional SWOT and MeanDRS volume anomalies slices
# for global comparison
# Author:
# Jeffrey Wade, 2024

# ******************************************************************************
# Import Python modules
# ******************************************************************************
import sys
import os
import re
import pandas as pd
import numpy as np
import geopandas as gpd
import glob
import xarray as xr
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# # ******************************************************************************
# # Set input file paths
# # ******************************************************************************
# # Set volume anomaly file path
# slice_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/MeanDRS_slice/'

# # Set output file path for volume anomalies slices
# slice_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/'\
#     'global_summary/MeanDRS_slice/MeanDRS_slice_global_summary.csv'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - slice_in
# 2 - slice_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 3:
    print('ERROR - 2 arguments must be used')
    raise SystemExit(22)

slice_in = sys.argv[1]
slice_out = sys.argv[2]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    if os.path.isdir(slice_in):
        pass
except IOError:
    print('ERROR - '+slice_in+' invalid folder path')
    raise SystemExit(22)


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# Volume Anomaly slices
# ------------------------------------------------------------------------------
# Read anomaly slices files
slice_files = sorted(list(glob.iglob(slice_in + '*.csv')))
slice_all = [pd.read_csv(x) for x in slice_files]


# ******************************************************************************
# Aggregate SWOT and MeanDRS volume anomaly slices across all regions
# ******************************************************************************
print('Aggregating volume anomaly slices globally')
# Calculate sum of SWOT and MeanDRS anomalies for each month
slice_df = sum([df.drop(columns=['mon']) for df in slice_all if not df.empty])

# Calculate 0-mean anomalies
slice_df = slice_df.sub(slice_df.mean())

# Insert month column
slice_df.insert(0, 'mon', slice_all[0]['mon'])

# Write to file
slice_df.to_csv(slice_out, index=False)
