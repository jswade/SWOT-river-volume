#!/usr/bin/env python3
# ******************************************************************************
# meandrs_volume_scale_global.py
# ******************************************************************************

# Purpose:
# Calculate volume anomalies at all MeanDRS reaches with MERIT-SWORD
# translations and at all MeanDRS reaches
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


# # ******************************************************************************
# # Set input file paths
# # ******************************************************************************
# # Set file path to SWORD to MeanDRS translations
# ms_in = '/Users/jwade/jpl/computing/swot_volume/input/MERIT-SWORD/'\
#     'ms_translate/sword_to_mb/sword_to_mb_pfaf_11_translate.nc'

# # Set file path to MERIT-Basins shapefiles
# mb_in = '/Users/jwade/jpl/computing/swot_volume/input/MERIT-Basins/'

# # Set file path to MeanDRS volume simulations
# mV_in = '/Users/jwade/jpl/computing/swot_volume/input/MeanDRS/cor/V/'

# # Set file path to SWORD reach file
# sword_in = '/Users/jwade/jpl/computing/swot_volume/input/SWORD/'\
#     'SWORD_reaches_v16/'

# # Set output file path for volume anomalies
# scale_anom_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/'\
#     'MeanDRS_scale/V_MeanDRS_scale_pfaf_11_2023-10-01_2024-09-30.csv'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - ms_in
# 2 - mb_in
# 3 - mV_in
# 4 - sword_in
# 5 - scale_anom_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 6:
    print('ERROR - 5 arguments must be used')
    raise SystemExit(22)

ms_in = sys.argv[1]
mb_in = sys.argv[2]
mV_in = sys.argv[3]
sword_in = sys.argv[4]
scale_anom_out = sys.argv[5]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    with open(ms_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + ms_in)
    raise SystemExit(22)

try:
    if os.path.isdir(mb_in):
        pass
except IOError:
    print('ERROR - '+mb_in+' invalid folder path')
    raise SystemExit(22)

try:
    if os.path.isdir(mV_in):
        pass
except IOError:
    print('ERROR - '+mV_in+' invalid folder path')
    raise SystemExit(22)

try:
    if os.path.isdir(sword_in):
        pass
except IOError:
    print('ERROR - '+sword_in+' invalid folder path')
    raise SystemExit(22)


# ******************************************************************************
# Define function for adding key: value to dictionary
# ******************************************************************************
# Add key to dictionary if it is not yet present
# If key already exists, add value to existing value at that key
def add_to_dict(dictionary, key, value):
    # Add to the existing value
    if key in dictionary:
        dictionary[key] += value
    # Initialize the key with the value
    else:
        dictionary[key] = value


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# MERIT-SWORD
# ------------------------------------------------------------------------------
# Read SWORD to MB translation
ms_df = xr.open_dataset(ms_in).to_dataframe()


# ******************************************************************************
# Retrieve MeanDRS volumes using weighted translations
# ******************************************************************************
print('Retrieving corresponding MeanDRS volumes')
# ------------------------------------------------------------------------------
# Load translations from relevant layers
# ------------------------------------------------------------------------------
# Retrieve SWORD reaches with valid translations
if len(ms_df) > 0:
    ms_sword = ms_df[ms_df.mb_1 != 0]
else:
    ms_sword = []

# Get unique translations, if they exist
if len(ms_sword) != 0:
    unique_trans = pd.concat([pd.Series(ms_sword.iloc[:, i].unique().
                                        astype('int'))
                              for i in range(40)]).unique()

# Else, write empty dataframes
else:
    scale_anom_tot = pd.DataFrame(columns=['empty'])
    scale_anom_tot.to_csv(scale_anom_out, index=False)

    # Exit with success code
    print('No corresponding MeanDRS reaches')
    sys.exit(0)

# Retrieve unique MB regions
regs = list(set([x//1000000 for x in unique_trans]))
regs = sorted([x for x in regs if x > 0])

# Retrieve index of main region of interest
main_ind = regs.index(int(ms_in.split('pfaf_')[1][0:2]))

# ------------------------------------------------------------------------------
# Load MeanDRS volume files from associated regions
# ------------------------------------------------------------------------------
# Load relevant MeanDRS volume files
mV_hig_in = [glob.glob(mV_in + '*_pfaf_' + str(x) + '*hig.nc4')[0] for
             x in regs]
mV_nrm_in = [glob.glob(mV_in + '*_pfaf_' + str(x) + '*nrm.nc4')[0] for
             x in regs]
mV_low_in = [glob.glob(mV_in + '*_pfaf_' + str(x) + '*low.nc4')[0] for
             x in regs]

# Read MeanDRS volume simulations
mV_hig = [xr.open_dataset(x) for x in mV_hig_in]
mV_nrm = [xr.open_dataset(x) for x in mV_nrm_in]
mV_low = [xr.open_dataset(x) for x in mV_low_in]

# Reformat MeanDRS times
mV_time = mV_low[0].time.values
date_range = pd.date_range(start=pd.Timestamp(mV_time[0]),
                           periods=len(mV_time),
                           freq='MS')
mon_range = date_range.month

# ------------------------------------------------------------------------------
# Load MERIT-Basins shapefiles from associated regions
# ------------------------------------------------------------------------------
# Load relevant MERIT-Basins shapefiles
mb_files = [glob.glob(mb_in + '*_pfaf_' + str(x) + '*.shp')[0] for x in regs]

# Read MERIT-Basins shapefiles
mb_shps = [gpd.read_file(x) for x in mb_files]

# Create dictionary of MERIT-Basins reach lengths (in meters)
mb_len = {}
for i in range(len(mb_shps)):
    mb_len.update((mb_shps[i].set_index('COMID')['lengthkm'] * 1000).to_dict())

# ------------------------------------------------------------------------------
# Load SWORD shapefiles from associated regions
# ------------------------------------------------------------------------------
# Load relevant SWORD shapefiles
sword_all = [glob.glob(sword_in + '*hb' + str(x) + '*.shp')[0] for
             x in regs]

# Read SWORD shapefile
sword_shps = [gpd.read_file(x) for x in sword_all]

# Create dictionary of SWORD reach lengths
sword_len = {}
for i in range(len(sword_shps)):
    sword_len.update(sword_shps[i].set_index('reach_id')['reach_len'].
                     to_dict())

# ------------------------------------------------------------------------------
# Calculate MeanDRS monthly volume anomaly
# ------------------------------------------------------------------------------
print('Calculating MeanDRS volume anomalies')
# Calculate volume anomaly time series at each reach (km3)
mV_hig_a_all = []
mV_nrm_a_all = []
mV_low_a_all = []
for i in range(len(regs)):
    mV_hig_a_all.append(1e-9 * (mV_hig[i].V - np.mean(mV_hig[i].V, axis=0)))
    mV_nrm_a_all.append(1e-9 * (mV_nrm[i].V - np.mean(mV_nrm[i].V, axis=0)))
    mV_low_a_all.append(1e-9 * (mV_low[i].V - np.mean(mV_low[i].V, axis=0)))

# ------------------------------------------------------------------------------
# Set length scaling factor
# ------------------------------------------------------------------------------
# MERIT-Basins are more sinuous than SWORD reaches, causing MERIT reaches to be
# ~1.1x longer than SWORD reaches. This complicates using overlapping SWORD lens
# to retrieve weighted MeanDRS volumes

# We derive a scaling factor between MERIT and SWORD reach lengths based on
# the total network lengths of MERIT-SWORD and SWORD (Wade et al., 2025)
# Global MERIT-SWORD len: 2448197.8 km
# Global SWORD len: 2172425.0 km
len_scale = 2448197.8 / 2172425

# ------------------------------------------------------------------------------
# Retrieve MeanDRS volumes using translation for Type 1/5 MERIT-SWORD reaches
# ------------------------------------------------------------------------------
print('Retrieve MeanDRS volume anomalies for reach subsets')
# Retrieve all SWORD reaches with translations
rch_sw = ms_sword.index.values

# Filter to Type 1/5 SWORD reaches
rch_type = rch_sw % 10
rch_sw = rch_sw[(rch_type == 1) | (rch_type == 5)]

# Initialize mb_reaches_sw
mb_reaches_sw = {}

# Loop through all SWORD reaches with translations
for i in range(len(rch_sw)):

    # Retrieve corresponding MB reaches, SWORD reach id, and SWORD length
    ms_trans = ms_sword.loc[rch_sw[i]]
    sw_len = sword_len[rch_sw[i]]

    # Loop through valid translations and their corresponding partial lens
    for k in range(len(ms_trans)):

        # Retrieve translation
        trans_k = ms_trans.iloc[k]

        # If no valid translation, skip reach
        if trans_k <= 0:
            break

        # If sw_len = 0, skip reach
        if sw_len == 0:
            break

        # Retrieve weight frac based on MB and SWORD intersecting lengths
        # Scale intersecting SWORD length beased on len_scale factor (~1.1x)
        weight = len_scale * ms_trans.iloc[k + 40] / mb_len[trans_k]

        # Add translation and weight to dictionary
        # If translation already exists, sum weights
        add_to_dict(mb_reaches_sw, float(trans_k), float(weight))

# ------------------------------------------------------------------------------
# Calculate MeanDRS volume anomaly for MERIT-SWORD Reaches
# ------------------------------------------------------------------------------
# Initalize dataframes to store MeanDRS monthly volumes anomalies
scale_anom_tot = pd.DataFrame(np.zeros((len(date_range), 3)),
                              columns=['mV_low_anom_ms',
                                       'mV_nrm_anom_ms',
                                       'mV_hig_anom_ms'],
                              index=date_range.date)
scale_anom_tot = scale_anom_tot.rename_axis("dates")

# Calculate MeanDRS volume totals for each month at MERIT-SWORD reaches
# Retrieve translations and weightings for MERIT-SWORD reaches
mb_rch_sw = np.array(list(mb_reaches_sw.keys()))
mb_weight_sw = np.array(list(mb_reaches_sw.values()))

# Set all weights larger than 1 to 1
mb_weight_sw[mb_weight_sw > 1] = 1

# Find regions of translated MB reaches
mb_ind_sw = np.array([regs.index(x // 1000000) for x in mb_reaches_sw])
uniq_ind_sw, inv_ind_sw = np.unique(mb_ind_sw, return_inverse=True)

# Retrieve volumes for all unique regions
for i in range(len(uniq_ind_sw)):

    # Retrieve reaches and weights for each region
    reg_reaches = mb_rch_sw[inv_ind_sw == i]
    reg_weight = mb_weight_sw[inv_ind_sw == i]

    # Weight MeanDRS volume values by translation overlap
    low_values = mV_low_a_all[uniq_ind_sw[i]].sel(
        rivid=reg_reaches).values * reg_weight
    nrm_values = mV_nrm_a_all[uniq_ind_sw[i]].sel(
        rivid=reg_reaches).values * reg_weight
    hig_values = mV_hig_a_all[uniq_ind_sw[i]].sel(
        rivid=reg_reaches).values * reg_weight

    # Sum MeanDRS volume anomaly
    scale_anom_tot.mV_low_anom_ms += np.sum(low_values, axis=1)
    scale_anom_tot.mV_nrm_anom_ms += np.sum(nrm_values, axis=1)
    scale_anom_tot.mV_hig_anom_ms += np.sum(hig_values, axis=1)

# ------------------------------------------------------------------------------
# Write volume anomalies to file
# ------------------------------------------------------------------------------
print('Writing files')
scale_anom_tot.to_csv(scale_anom_out, index=True)
