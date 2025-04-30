#!/usr/bin/env python3
# ******************************************************************************
# swot_num_obs.py
# ******************************************************************************

# Purpose:
# Calculate the number of reaches with valid SWOT volume computations
# Author:
# Jeffrey Wade, 2024

# ******************************************************************************
# Import Python modules
# ******************************************************************************
import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
import glob
import xarray as xr
import matplotlib.pyplot as plt


## ******************************************************************************
## Set input file paths
## ******************************************************************************
## Set volume anomaly file path
#V_anom_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/V_anom/'
#
## Set file path to SWORD to MeanDRS translations
#ms_in = '/Users/jwade/jpl/computing/swot_volume/input/MERIT-SWORD/'\
#    'ms_translate/sword_to_mb/'
#
## Set file path to SWORD reach file
#sword_in = '/Users/jwade/jpl/computing/swot_volume/input/SWORD/'\
#    'SWORD_reaches_v16/'
#
#obs_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/n_obs/'\
#    'swot_n_obs.csv'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - V_anom_in
# 2 - ms_in
# 3 - sword_in
# 4 - obs_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 5:
    print('ERROR - 4 arguments must be used')
    raise SystemExit(22)

V_anom_in = sys.argv[1]
ms_in = sys.argv[2]
sword_in = sys.argv[3]
obs_out = sys.argv[4]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    if os.path.isdir(V_anom_in):
        pass
except IOError:
    print('ERROR - '+V_anom_in+' invalid folder path')
    raise SystemExit(22)

try:
    if os.path.isdir(ms_in):
        pass
except IOError:
    print('ERROR - '+ms_in+' invalid folder path')
    raise SystemExit(22)

try:
    if os.path.isdir(sword_in):
        pass
except IOError:
    print('ERROR - '+sword_in+' invalid folder path')
    raise SystemExit(22)


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# Volume
# ------------------------------------------------------------------------------
# Read V anomaly files
V_anom_files = sorted(list(glob.iglob(V_anom_in + '*.csv')))
V_anom_all = [pd.read_csv(x, index_col='reach_id') for x in V_anom_files]

# Convert columns to dates
for i in range(len(V_anom_all)):
    V_anom_all[i].columns = pd.to_datetime(V_anom_all[i].columns)

# Get pfaf numbers
pfaf_list = [x.split('pfaf_')[1][0:2] for x in V_anom_files]

# ------------------------------------------------------------------------------
# MERIT-SWORD
# ------------------------------------------------------------------------------
# Read SWORD to MB translations
ms_files = sorted(list(glob.iglob(ms_in + '*.nc')))
ms_all = [xr.open_dataset(x).to_dataframe() for x in ms_files]

# ------------------------------------------------------------------------------
# SWORD
# ------------------------------------------------------------------------------
# Read SWORD shapefiles
sword_files = sorted(list(glob.iglob(sword_in + '*.shp')))

# Retrieve pfaf numbers from file
sw_pfaf_list = pd.Series([x.partition("reaches_hb")[-1][0:2]
                          for x in sword_files]).sort_values()

# Sort files by pfaf to align with MERIT-Basins
sword_files = pd.Series(sword_files)[sw_pfaf_list.index.values].tolist()

# Load SWORD shapefiles
sword_all = [gpd.read_file(x) for x in sword_files]

# Add empty dataframe at pfaf 35
sword_all.insert(35, pd.DataFrame())


# ******************************************************************************
# Retrieve number of observations with V_anom and translation in each region
# ******************************************************************************
print('Retrieving valid observations')

# Initialize dataframe
obs_df = pd.DataFrame({'pfaf': pfaf_list,
                       'sword': np.repeat(0, len(pfaf_list)),
                       'sw_type1': np.repeat(0, len(pfaf_list)),
                       'V_anom': np.repeat(0, len(pfaf_list)),
                       'V_anom_ms': np.repeat(0, len(pfaf_list))})

for i in range(len(V_anom_all)):

    # Retrieve relevant files
    V_anom = V_anom_all[i]
    ms_df = ms_all[i]
    sword_i = sword_all[i]

    # If no SWORD reaches, skip region
    if len(sword_i) == 0:
        continue

    # Retrieve sword reach types
    rch_type = sword_i.reach_id % 10

    # Store number of sword reaches (not type 6)
    obs_df.loc[i, 'sword'] = len(sword_i[rch_type != 6])

    # Store number of type 1 sword reaches
    # obs_df.loc[i, 'sw_type1'] = len(sword_i[rch_type == 1])
    obs_df.loc[i, 'sw_type1'] = (rch_type.isin([1, 5])).sum()

    # Store number of V_anom reaches (> 5 obs, type 1)
    obs_df.loc[i, 'V_anom'] = len(V_anom)

    # Retrieve translations corresponding to volume observations
    ms_swot = ms_df.loc[ms_df.index.isin(V_anom.index.values)]

    # If no V anomalies, skip region
    if len(ms_swot) == 0:
        continue

    # Drop values from if no translation exists
    ms_swot = ms_swot[ms_swot.mb_1 != 0]

    # Store number of V anonm reaches with translation
    obs_df.loc[i, 'V_anom_ms'] = len(ms_swot)

# Sort based on number of SWORD reaches
obs_df = obs_df.sort_values(by="sword", ascending=True).reset_index(drop='True')

# Plot bar plot of number of reaches observed
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 12
plt.figure(figsize=(12, 6))
plt.bar(np.arange(len(obs_df)), obs_df.sword, width=0.6, color='#9E95CB',
        edgecolor='black', label="All SWORD Reaches", zorder=1)
plt.bar(np.arange(len(obs_df)), obs_df.sw_type1, width=0.6, color='#FF463B',
        edgecolor='black', label="Sword Type 1+5 Reaches", zorder=2)
plt.bar(np.arange(len(obs_df)), obs_df.V_anom, width=0.6, color='#1741bf',
        edgecolor='black', label="Obs. SWORD Reaches", zorder=3)
plt.bar(np.arange(len(obs_df)), obs_df.V_anom_ms, width=0.6, color='#3FB9DE',
        edgecolor='black', label="Obs. SWORD Reaches with Translation",
        zorder=3)
plt.xlim([-.5, 60.5])
plt.ylim([0, 20000])
plt.ylabel('Number of Reaches', fontsize=13)
plt.xlabel('Pfaf Region', fontsize=13)
plt.xticks(ticks=np.arange(len(obs_df)), labels=obs_df.pfaf, rotation=90)
plt.legend()
plt.show()

# Write to file
obs_df.to_csv(obs_out, index=False)
