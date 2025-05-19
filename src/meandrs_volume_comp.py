#!/usr/bin/env python3
# ******************************************************************************
# meandrs_volume_comp.py
# ******************************************************************************

# Purpose:
# Compare MeanDRS river volume to SWOT observations using MERIT-SWORD
# Retains raw monthly volume anomalies so that global means and std can be
# calculated
# Author:
# Jeffrey Wade, 2024

# ******************************************************************************
# Import Python modules
# ******************************************************************************
import sys
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import glob
import xarray as xr


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - V_anom_in
# 2 - ms_in
# 3 - mb_in
# 4 - mV_in
# 5 - sword_in
# 6 - sword_anom_out
# 7 - meandrs_anom_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 8:
    print('ERROR - 7 arguments must be used')
    raise SystemExit(22)

V_anom_in = sys.argv[1]
ms_in = sys.argv[2]
mb_in = sys.argv[3]
mV_in = sys.argv[4]
sword_in = sys.argv[5]
swot_anom_out = sys.argv[6]
meandrs_anom_out = sys.argv[7]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    with open(V_anom_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + V_anom_in)
    raise SystemExit(22)

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
# Volume
# ------------------------------------------------------------------------------
# Read V anomaly files
V_anom = pd.read_csv(V_anom_in, index_col='reach_id')

# Convert columns to dates
V_anom.columns = pd.to_datetime(V_anom.columns)

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
# Load MeanDRS volume files from associated regions
# ------------------------------------------------------------------------------
# Retrieve reaches corresponding to volume observations
ms_swot = ms_df.loc[ms_df.index.isin(V_anom.index.values)]

# Get unique translations, if they exist
if len(ms_swot) != 0:
    unique_trans = pd.concat([pd.Series(ms_swot.iloc[:, i].unique().
                                        astype('int'))
                              for i in range(41)]).unique()
# Else, write empty dataframes
else:
    V_anom_tot = pd.DataFrame(columns=['empty'])
    meandrs_anom_tot = pd.DataFrame(columns=['empty'])

    V_anom_tot.to_csv(swot_anom_out, index=False)
    meandrs_anom_tot.to_csv(meandrs_anom_out, index=False)

    # Exit with success code
    print('No corresponding MeanDRS reaches')
    sys.exit(0)

# Retrieve unique MB regions
regs = list(set([x//1000000 for x in unique_trans]))
regs = sorted([x for x in regs if x > 0])

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
# Retrieve MeanDRS volumes using weighted translation
# ------------------------------------------------------------------------------
# Initalize lists to store MB translations and reaches without translation
mb_reaches = []
rch_drop = []

# Retrieve SWORD reaches observed in each month
rch_obs = [V_anom[V_anom[col].notna()].index.tolist() for
           col in V_anom.columns]

# Reformat MeanDRS times
mV_time = mV_low[0].time.values
date_range = pd.date_range(start=pd.Timestamp(mV_time[0]),
                           periods=len(mV_time),
                           freq='MS')
mon_range = date_range.month

# Loop through months
for i in range(len(V_anom.columns)):

    # Initialize rch_drop_i and mb_reaches_i
    rch_drop_i = []
    mb_reaches_i = {}

    # Select observed SWORD reaches
    rch_i = rch_obs[i]

    # Loop through observed SWORD reaches
    for k in range(len(rch_i)):

        # Retrieve corresponding MB reaches, SWORD reach id, and SWORD len
        ms_trans = ms_swot.loc[rch_i[k]]
        sw_len = sword_len[rch_i[k]]

        # If reach has no translation, drop SWOT volume at reach
        if ms_trans.mb_1 == 0:
            rch_drop_i.append(rch_i[k])
            continue

        # Loop through valid translations and their corresponding part. len
        for t in range(len(ms_trans)):

            # Retrieve translation
            trans_t = ms_trans.iloc[t]

            # If no valid translation, exit loop
            if trans_t <= 0:
                break

            # Retrieve weight frac based on MB and SWORD intersecting lengths
            # Scale intersecting SWORD length beased on len_scale factor (~1.1x)
            weight = len_scale * ms_trans.iloc[t + 40] / mb_len[trans_t]

            # Add translation and weight to dictionary
            # If translation already exists, sum weights
            add_to_dict(mb_reaches_i, float(trans_t), float(weight))

    # Append mb_reaches_i and rch_drop_i
    mb_reaches.append(mb_reaches_i)
    rch_drop.extend(rch_drop_i)

# ------------------------------------------------------------------------------
# Calculate MeanDRS monthly volume anomaly
# ------------------------------------------------------------------------------
print('Calculating MeanDRS volume anomalies')
# For each region, calculate volume anomaly time series at each reach (km3)
mV_hig_a_all = []
mV_nrm_a_all = []
mV_low_a_all = []

for i in range(len(regs)):
    mV_hig_a_all.append(1e-9 * (mV_hig[i].V - np.mean(mV_hig[i].V, axis=0)))
    mV_nrm_a_all.append(1e-9 * (mV_nrm[i].V - np.mean(mV_nrm[i].V, axis=0)))
    mV_low_a_all.append(1e-9 * (mV_low[i].V - np.mean(mV_low[i].V, axis=0)))

# Initialize arrays to store weighted MeanDRS volumes for each months
mV_low_mon = pd.Series(np.zeros(len(mon_range)))
mV_nrm_mon = pd.Series(np.zeros(len(mon_range)))
mV_hig_mon = pd.Series(np.zeros(len(mon_range)))

# Calculate MeanDRS volume totals for each month
for i in range(len(V_anom.columns)):

    # Retrieve month of SWOT observation
    swot_mon = V_anom.columns[i].month

    # Find indices of MeanDRS observations that match month of SWOT obs
    mon_ind = np.where(mon_range == swot_mon)[0]

    # Retrieve translations and weightings for given month
    mb_rch_i = np.array(list(mb_reaches[i].keys()))
    mb_weight_i = np.array(list(mb_reaches[i].values()))

    # Set all weights larger than 1 to 1
    mb_weight_i[mb_weight_i > 1] = 1

    # Find regions of translated MB reaches
    mb_ind = np.array([regs.index(x // 1000000) for x in mb_reaches[i]])
    uniq_ind, inv_ind = np.unique(mb_ind, return_inverse=True)

    # Initialize arrays for storing volumes
    mV_hig_i = np.zeros(len(mon_ind))
    mV_nrm_i = np.zeros(len(mon_ind))
    mV_low_i = np.zeros(len(mon_ind))

    # Retrieve volumes for all unique regions
    for k in range(len(uniq_ind)):

        # Retrieve reaches and weights for each region
        reg_reaches = mb_rch_i[inv_ind == k]
        reg_weight = mb_weight_i[inv_ind == k]

        # Retrieve MeanDRS volume values for month of interest (V anomaly),
        # weighting by translation overlap
        hig_values = mV_hig_a_all[uniq_ind[k]].sel(rivid=reg_reaches).\
            isel(time=mon_ind).values * reg_weight
        nrm_values = mV_nrm_a_all[uniq_ind[k]].sel(rivid=reg_reaches).\
            isel(time=mon_ind).values * reg_weight
        low_values = mV_low_a_all[uniq_ind[k]].sel(rivid=reg_reaches).\
            isel(time=mon_ind).values * reg_weight

        # Sum MeanDRS volume anomaly
        mV_hig_i += np.sum(hig_values, axis=1)
        mV_nrm_i += np.sum(nrm_values, axis=1)
        mV_low_i += np.sum(low_values, axis=1)

    # Store monthly volume anomalies
    mV_low_mon[mon_ind] = mV_low_i
    mV_nrm_mon[mon_ind] = mV_nrm_i
    mV_hig_mon[mon_ind] = mV_hig_i

# ------------------------------------------------------------------------------
# Summarize SWOT volume anomaly
# ------------------------------------------------------------------------------
# Drop rows from V_anom without translations
V_anom_drop = V_anom.drop(index=np.unique(rch_drop))

# Calculate SWOT volume total for each month
V_anom_tot = np.sum(V_anom_drop, axis=0)

# Count number of reaches in each monthly sum
V_anom_ct = V_anom_drop.notna().sum()

# Reformat SWOT columns
V_anom_tot = V_anom_tot.rename('V_SWOT')
V_anom_tot = V_anom_tot.reset_index().\
    rename(columns={'index': 'dates'})

# ------------------------------------------------------------------------------
# Summarize MeanDRS volume anomaly
# ------------------------------------------------------------------------------
# Calculate 0-mean anomalyies
mV_low_mon_a = mV_low_mon - np.mean(mV_low_mon)
mV_nrm_mon_a = mV_nrm_mon - np.mean(mV_nrm_mon)
mV_hig_mon_a = mV_hig_mon - np.mean(mV_hig_mon)

# Assemble dataframe of MeanDRS volume anomalies
meandrs_anom_tot = pd.concat([mV_hig_mon_a, mV_nrm_mon_a, mV_low_mon_a], axis=1)
meandrs_anom_tot.index = date_range
meandrs_anom_tot.index = meandrs_anom_tot.index.date
meandrs_anom_tot.columns = ['mV_hig_anom', 'mV_nrm_anom', 'mV_low_anom']
meandrs_anom_tot = meandrs_anom_tot.rename_axis("dates")

# ------------------------------------------------------------------------------
# Write volume anomalies to file
# ------------------------------------------------------------------------------
print('Writing files')
# Write SWOT anomaly to file
V_anom_tot.to_csv(swot_anom_out, index=False)

# Write MeanDRS anomaly to file
meandrs_anom_tot.to_csv(meandrs_anom_out, index=True)
