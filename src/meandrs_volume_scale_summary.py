#!/usr/bin/env python3
# ******************************************************************************
# meandrs_volume_scale_summary.py
# ******************************************************************************

# Purpose:
# Aggregate regional SWOT and scaled MeanDRS volume anomalies for
# global comparison
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
import matplotlib.pyplot as plt


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - swot_anom_in
# 2 - meandrs_anom_in
# 3 - scale_anom_in
# 4 - scale_reg_out
# 5 - scale_global_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 6:
    print('ERROR - 5 arguments must be used')
    raise SystemExit(22)

swot_anom_in = sys.argv[1]
meandrs_anom_in = sys.argv[2]
scale_anom_in = sys.argv[3]
scale_reg_out = sys.argv[4]
scale_global_out = sys.argv[5]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    if os.path.isdir(swot_anom_in):
        pass
except IOError:
    print('ERROR - '+swot_anom_in+' invalid folder path')
    raise SystemExit(22)

try:
    if os.path.isdir(meandrs_anom_in):
        pass
except IOError:
    print('ERROR - '+meandrs_anom_in+' invalid folder path')
    raise SystemExit(22)

try:
    if os.path.isdir(scale_anom_in):
        pass
except IOError:
    print('ERROR - '+scale_anom_in+' invalid folder path')
    raise SystemExit(22)


# ******************************************************************************
# Define functions
# ******************************************************************************
# Define function for least-squares scaling, where x is smaller magnitude
# time series
# Finds alpha to best match Y = a * X, where X and Y are vol. anomalies
def ls_scale(x, y):
    # If denominator is 0, scaling factor can't be computed, return 1
    if np.sum(x ** 2) == 0:
        return 1
    return np.sum(x * y) / np.sum(x ** 2)


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# Volume Anomalies
# ------------------------------------------------------------------------------
# Read SWOT anomaly files
swot_anom_files = sorted(list(glob.iglob(swot_anom_in + '*.csv')))
swot_anom_all = [pd.read_csv(x) for x in swot_anom_files]

# Read MeanDRS anomaly files
meandrs_anom_files = sorted(list(glob.iglob(meandrs_anom_in + '*.csv')))
meandrs_anom_all = [pd.read_csv(x) for x in meandrs_anom_files]

# Read MeanDRS scaled anomaly files
scale_anom_files = sorted(list(glob.iglob(scale_anom_in + '*.csv')))
scale_anom_all = [pd.read_csv(x) for x in scale_anom_files]

# Retrieve list of pfaf ids
pfaf_list = pd.Series([x.partition("pfaf_")[-1][0:2] for x in swot_anom_files])


# ******************************************************************************
# Aggregate SWOT and MeanDRS volume anomalies for each region
# ******************************************************************************
print('Scaling SWOT volume using MeanDRS volume subsets')
# Retrieve dates from SWOT observations
swot_dates = swot_anom_all[0].dates

global_scale_df = pd.DataFrame(np.zeros((len(swot_dates), 5)),
                               columns=['dates',
                                        'V_SWOT',
                                        'mV_low_anom_swot',
                                        'mV_low_anom_ms',
                                        'V_SWOT_ms'])
global_scale_df.dates = swot_dates

# Initialize list to store scaling factors
ls_scale_list = []

# Initialize list to store scale_dfs
scale_list = []

for j in range(len(pfaf_list)):

    # Initialize dataframe to store values
    scale_df = swot_anom_all[j].copy()

    # Set output file path
    scale_fp = scale_reg_out + 'V_MeanDRS_scale_means_pfaf_' + \
        pfaf_list[j] + '_2023-10-01_2024-09-30.csv'

    # If no values in scale_df, write empty dataframe
    if len(scale_df) == 0:

        scale_df = pd.DataFrame(columns=['dates',
                                         'V_SWOT',
                                         'mV_low_anom_swot',
                                         'mV_low_anom_ms',
                                         'V_SWOT_ms'])
        scale_df.to_csv(scale_fp, index=False)
        continue

    # Retrieve SWOT and MeanDRS volume anomalies
    meandrs_anom_j = meandrs_anom_all[j]
    scale_anom_j = scale_anom_all[j]
    swot_anom_j = swot_anom_all[j]

    # Convert dates to months
    meandrs_anom_j['mon'] = pd.to_datetime(meandrs_anom_j.dates).dt.month
    scale_anom_j['mon'] = pd.to_datetime(scale_anom_j.dates).dt.month

    # Summarize MeanDRS volume anomalies representing SWOT obs for each month
    meandrs_low_swot = meandrs_anom_j.groupby('mon').agg({
        'mV_low_anom': ['mean']})

    # Reorder to match months of swot_anom_j and insert into dataframe
    month_order = pd.to_datetime(swot_anom_j.dates).dt.month.values
    meandrs_low_swot = meandrs_low_swot.reindex(month_order)
    scale_df['mV_low_anom_swot'] = meandrs_low_swot.values

    # Summarize MeanDRS volume anomalies for each month for MERIT-SWORD reaches
    meandrs_low_scale = scale_anom_j.groupby('mon').agg({
        'mV_low_anom_ms': ['mean']})

    # Reorder to match months of swot_anom_j and insert into dataframe
    meandrs_low_scale = meandrs_low_scale.reindex(month_order)
    scale_df['mV_low_anom_ms'] = meandrs_low_scale.iloc[:, 0].values

    # Calculate 0-mean anomalies
    scale_df.iloc[:, 1:] = scale_df.iloc[:, 1:].sub(scale_df.iloc[:, 1:].mean())

    # Calculate least-squares scaling factors between MeanDRS anomalies
    # Finds alpha to best match Y = a * X, where X and Y are vol. anomalies
    ms_scale = ls_scale(scale_df.mV_low_anom_swot, scale_df.mV_low_anom_ms)

    # Scale observed SWOT volume anomaly to account for unobserved SWORD reaches
    # and MERIT-Basins reaches not in SWORD
    scale_df['V_SWOT_ms'] = scale_df.V_SWOT * ms_scale

    # Add scale_df to global_scale_df
    global_scale_df.iloc[:, 1:] += scale_df.iloc[:, 1:]

    # Store scale_df
    scale_list.append(scale_df)

    # Write to file
    scale_df.to_csv(scale_fp, index=False)

# Write global_scale_df to file
global_scale_df.to_csv(scale_global_out, index=False)
