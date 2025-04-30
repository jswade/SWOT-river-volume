#!/usr/bin/env python3
# ******************************************************************************
# swot_volume_reach_shp.py
# ******************************************************************************

# Purpose:
# Plot comparisons between SWOT and MeanDRS volumes.
# Author:
# Jeffrey Wade, 2024

# ******************************************************************************
# Import Python modules
# ******************************************************************************
import os
import sys
import pandas as pd
import numpy as np
import glob
import geopandas as gpd

#
## ******************************************************************************
## Set input file paths
## ******************************************************************************
## Set input file path for volume anomalies
#anom_reg_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/V_anom/'
#
#sword_in = '/Users/jwade/jpl/computing/swot_volume/input/SWORD/'\
#    'SWORD_reaches_v16/'
#
#sword_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/'\
#    'SWORD_reach_anom/'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - anom_reg_in
# 2 - sword_in
# 3 - sword_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 4:
    print('ERROR - 3 arguments must be used')
    raise SystemExit(22)

anom_reg_in = sys.argv[1]
sword_in = sys.argv[2]
sword_out = sys.argv[3]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    if os.path.isdir(anom_reg_in):
        pass
except IOError:
    print('ERROR - '+anom_reg_in+' invalid folder path')
    raise SystemExit(22)

try:
    with open(sword_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + sword_in)
    raise SystemExit(22)

try:
    if os.path.isdir(sword_out):
        pass
except IOError:
    print('ERROR - '+sword_out+' invalid folder path')
    raise SystemExit(22)


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# SWOT Observed Volume Anomalies
# ------------------------------------------------------------------------------
# Read regional anomaly files
anom_reg_files = sorted(list(glob.iglob(anom_reg_in + '*.csv')))
anom_reg_all = [pd.read_csv(x) for x in anom_reg_files]

# Retrieve pfaf regions of files
pfaf_list = pd.Series([x.partition("pfaf_")[-1][0:2] for x in anom_reg_files])

# ------------------------------------------------------------------------------
# SWORD Shapefiles
# ------------------------------------------------------------------------------
# Read regional SWORD files
sword_files = sorted(list(glob.iglob(sword_in + '*.shp')))

# Retrieve pfaf numbers from file
sw_pfaf_list = pd.Series([x.partition("reaches_hb")[-1][0:2]
                          for x in sword_files]).sort_values()

# Sort files by pfaf to align with SWOT observed files
sword_files = pd.Series(sword_files)[sw_pfaf_list.index.values].tolist()

# Load SWORD files as shapefiles
sword_all = [gpd.read_file(x) for x in sword_files]

# Add placeholder file at pfaf 54 for missing file
sword_all.insert(35, [])
sword_files.insert(35, [])

# ******************************************************************************
# Calculate volume anomaly amplitude at each reach
# ******************************************************************************
for i in range(len(sword_all)):

    print(i)

    # Retrieve SWOT volume and SWORD shapefile
    anom_i = anom_reg_all[i]
    sword_i = sword_all[i]

    # Skip empty regions
    if len(anom_i) == 0 or len(sword_i) == 0:
        continue

    # Create columns to store volume amplitude and timing
    sword_i['vol_amp'] = np.nan
    sword_i['vol_time'] = np.nan
    sword_i['vol_seas'] = np.nan

    # Calculate volume amplitude at each reach
    amp_i = anom_i.iloc[:, 1:].max(axis=1) - anom_i.iloc[:, 1:].min(axis=1)
    amp_i.index = anom_i.reach_id

    # Find the month where each reach has its maximum volume anomaly
    max_vol = anom_i.iloc[:, 1:].idxmax(axis=1).str[-2:].astype(int)
    max_vol.index = anom_i.reach_id

    # Set reach_id to sword_i index
    sword_i = sword_i.set_index('reach_id')

    # Assign volume amplitude and timing
    sword_i.loc[amp_i.index, 'vol_amp'] = amp_i
    sword_i.loc[max_vol.index, 'vol_time'] = max_vol

    # Categorize seasons
    sword_i.loc[sword_i['vol_time'].isin([12, 1, 2]), 'vol_seas'] = 1
    sword_i.loc[sword_i['vol_time'].isin([3, 4, 5]), 'vol_seas'] = 2
    sword_i.loc[sword_i['vol_time'].isin([6, 7, 8]), 'vol_seas'] = 3
    sword_i.loc[sword_i['vol_time'].isin([9, 10, 11]), 'vol_seas'] = 4

    # Reset index
    sword_i = sword_i.reset_index()

    # Reproject to Robinson
    robinson_proj = '+proj=robin +lon_0=0 +x_0=0 +y_0=0'\
        ' +datum=WGS84 +units=m +no_defs'
    sword_i.to_crs(robinson_proj)

    # Write to file
    fp_out = sword_out + 'SWORD_obs_anom_pfaf_' + pfaf_list[i] + '.shp'
    sword_i.to_file(fp_out)
