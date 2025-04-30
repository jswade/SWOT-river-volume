#!/usr/bin/env python3
# ******************************************************************************
# meandrs_volume_slice_global.py
# ******************************************************************************

# Purpose:
# Compare MeanDRS river volume to SWOT observations using MERIT-SWORD in yearly
# slices
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
# # Set volume anomaly file path
# V_anom_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/V_anom/'\
#     'V_anom_pfaf_11_2023-10-01_2024-09-30.csv'

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

# # Set output filepath
# slice_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/'\
#     'MeanDRS_slice/V_MeanDRS_slice_pfaf_11_2023-10-01_2024-09-30.csv'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - V_anom_in
# 2 - ms_in
# 3 - mb_in
# 4 - mV_in
# 5 - sword_in
# 6 - slice_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 7:
    print('ERROR - 6 arguments must be used')
    raise SystemExit(22)

V_anom_in = sys.argv[1]
ms_in = sys.argv[2]
mb_in = sys.argv[3]
mV_in = sys.argv[4]
sword_in = sys.argv[5]
slice_out = sys.argv[6]


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
# Load translations from relevant layers
# ------------------------------------------------------------------------------
# Retrieve reaches corresponding to volume observations
ms_swot = ms_df.loc[ms_df.index.isin(V_anom.index.values)]

# Get unique translations, if they exist
if len(ms_swot) != 0:
    unique_trans = pd.concat([pd.Series(ms_swot.iloc[:, i].unique().
                                        astype('int'))
                              for i in range(41)]).unique()
# Else, write empty dataframe
else:
    slice_df = pd.DataFrame(columns=['empty'])
    slice_df.to_csv(slice_out, index=False)

    # Exit with success code
    print('No corresponding MeanDRS reaches')
    sys.exit(0)

# Retrieve unique MB regions
regs = list(set([x//1000000 for x in unique_trans]))
regs = sorted([x for x in regs if x > 0])

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

# Read sword shapefile
sword_shps = [gpd.read_file(x) for x in sword_all]

# Create dictionary of sword reach lengths
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
# Calculate MeanDRS monthly volume anomaly by yearly slices
# ------------------------------------------------------------------------------
print('Calculating MeanDRS volume anomaly yearly slices')
# Retrieve yearly slices within 30 year record that align with SWOT months
start = np.where(mon_range == V_anom.columns[0].month)[0][0]
step = 12
stop = np.where(mon_range == V_anom.columns[11].month)[0][1] + 1
slice_ind = []
slice_date = []
while stop <= 360:
    slice_ind.append([int(start), int(stop)])
    slice_date.append(date_range[start].strftime('%Y-%m') + '_' +
                      date_range[stop].strftime('%Y-%m'))
    start += step
    stop += step

# Initialize arrays to store weighted MeanDRS volumes for each month slice
mV_low_sl = pd.DataFrame(np.zeros((len(slice_date), step)))
mV_nrm_sl = pd.DataFrame(np.zeros((len(slice_date), step)))
mV_hig_sl = pd.DataFrame(np.zeros((len(slice_date), step)))

# Loop through MeanDRS month slices
for k in range(len(slice_ind)):

    # Retrieve start and end slice_ind
    s_i = slice_ind[k][0]
    e_i = slice_ind[k][1]

    # For each region, calculate volume anomaly time series at each reach
    # for the given month slice (km3)
    mV_hig_a_all = []
    mV_nrm_a_all = []
    mV_low_a_all = []
    for i in range(len(regs)):
        mV_hig_a_all.append(1e-9 *
                            (mV_hig[i].isel(time=slice(s_i, e_i)).V -
                             np.mean(mV_hig[i].isel(time=slice(s_i, e_i)).V,
                                     axis=0)))
        mV_nrm_a_all.append(1e-9 *
                            (mV_nrm[i].isel(time=slice(s_i, e_i)).V -
                             np.mean(mV_nrm[i].isel(time=slice(s_i, e_i)).V,
                                     axis=0)))

        mV_low_a_all.append(1e-9 *
                            (mV_low[i].isel(time=slice(s_i, e_i)).V -
                             np.mean(mV_low[i].isel(time=slice(s_i, e_i)).V,
                                     axis=0)))

    # Set mon_range to current month slice
    mon_slice = mon_range[s_i:e_i]

    # Calculate  MeanDRS volume totals for each month
    for i in range(len(V_anom.columns)):

        # Retrieve month of SWOT observation
        swot_mon = V_anom.columns[i].month

        # Retrieve translations and weightings for given month
        mb_rch_i = np.array(list(mb_reaches[i].keys()))
        mb_weight_i = np.array(list(mb_reaches[i].values()))

        # Set all weights larger than 1 to 1
        mb_weight_i[mb_weight_i > 1] = 1

        # Find regions of translated MB reaches
        mb_ind = np.array([regs.index(x // 1000000) for x in mb_reaches[i]])
        uniq_ind, inv_ind = np.unique(mb_ind, return_inverse=True)

        # Initialize values for storing volumes
        mV_hig_i = 0
        mV_nrm_i = 0
        mV_low_i = 0

        # Retrieve volumes for all unique regions
        for t in range(len(uniq_ind)):

            # Retrieve reaches and weights for each region
            reg_reaches = mb_rch_i[inv_ind == t]
            reg_weight = mb_weight_i[inv_ind == t]

            # Retrieve MeanDRS volume values for month of interest
            # weighting by translation overlap
            hig_values = mV_hig_a_all[uniq_ind[t]].sel(rivid=reg_reaches).\
                isel(time=i).values * reg_weight
            nrm_values = mV_nrm_a_all[uniq_ind[t]].sel(rivid=reg_reaches).\
                isel(time=i).values * reg_weight
            low_values = mV_low_a_all[uniq_ind[t]].sel(rivid=reg_reaches).\
                isel(time=i).values * reg_weight

            # Sum MeanDRS volume anomaly
            mV_hig_i += np.sum(hig_values)
            mV_nrm_i += np.sum(nrm_values)
            mV_low_i += np.sum(low_values)

        # Store monthly volume anomalies
        mV_low_sl.iloc[k, i] = mV_low_i
        mV_nrm_sl.iloc[k, i] = mV_nrm_i
        mV_hig_sl.iloc[k, i] = mV_hig_i

# ------------------------------------------------------------------------------
# Calculate SWOT volume anomaly
# ------------------------------------------------------------------------------
print('Calculating SWOT volume anomaly')
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
# Write volume anomaly slices to file
# ------------------------------------------------------------------------------
print('Writing files')
# Combine SWOT and MeanDRS volume anomalies for output
slice_df = pd.concat([V_anom_tot, mV_hig_sl.T,
                      mV_nrm_sl.T, mV_low_sl.T], axis=1)

# Rename columns
yr_strs = [x[0:4] for x in slice_date]
slice_df.columns = ['mon', 'V_SWOT'] +\
    ['mV_hig_' + x for x in yr_strs] +\
    ['mV_nrm_' + x for x in yr_strs] +\
    ['mV_low_' + x for x in yr_strs]

# Write to file
slice_df.to_csv(slice_out, index=False)
