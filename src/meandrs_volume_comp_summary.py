#!/usr/bin/env python3
# ******************************************************************************
# meandrs_volume_comp_summary.py
# ******************************************************************************

# Purpose:
# Aggregate regional SWOT and MeanDRS volume anomalies for
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
# 3 - comp_reg_out
# 4 - comp_global_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 5:
    print('ERROR - 4 arguments must be used')
    raise SystemExit(22)

swot_anom_in = sys.argv[1]
meandrs_anom_in = sys.argv[2]
comp_reg_out = sys.argv[3]
comp_global_out = sys.argv[4]


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

# Retrieve list of pfaf ids
pfaf_list = pd.Series([x.partition("pfaf_")[-1][0:2] for x in swot_anom_files])


# ******************************************************************************
# Aggregate SWOT and MeanDRS volume anomalies for each region
# ******************************************************************************
print('Aggregating volume anomalies regionally')
# Retrieve dates from SWOT observations
swot_dates = swot_anom_all[0].dates

# Initialize dataframe to store values
comp_df = pd.DataFrame(np.zeros((len(swot_dates), 9)),
                       columns=['dates',
                                'mon',
                                'V_SWOT',
                                'mV_low_anom_mean',
                                'mV_low_anom_std',
                                'mV_nrm_anom_mean',
                                'mV_nrm_anom_std',
                                'mV_hig_anom_mean',
                                'mV_hig_anom_std',])
comp_df.dates = swot_dates
comp_df.mon = [x.month for x in pd.to_datetime(swot_dates)]

# Initialize list to store regional comparisons
reg_list = []

# Loop through regions
for j in range(len(pfaf_list)):

    print(j)

    # Retrieve SWOT and MeanDRS volume anomalies
    meandrs_anom_j = meandrs_anom_all[j].copy()
    swot_anom_j = swot_anom_all[j].copy()

    # Initialize dataframe to store regional summary values
    reg_df = comp_df.copy()

    # Set output file path
    comp_fp = comp_reg_out + 'V_MeanDRS_comp_means_pfaf_' + \
        pfaf_list[j] + '_2023-10-01_2024-09-30.csv'

    # If no values in comp_j, write empty dataframe
    if len(swot_anom_j) == 0:
        reg_df.to_csv(comp_fp, index=False)
        continue

    # Convert MeanDRS dates to months
    meandrs_anom_j['mon'] = pd.to_datetime(meandrs_anom_j.dates).dt.month

    # Summarize MeanDRS volume anomalies representing SWOT obs for each month
    meandrs_summary = meandrs_anom_j.groupby('mon').agg({
        'mV_low_anom': ['mean', 'std'],
        'mV_nrm_anom': ['mean', 'std'],
        'mV_hig_anom': ['mean', 'std']})
    meandrs_summary.columns = ['_'.join(col).strip()
                               for col in meandrs_summary.columns]

    # Reorder to match months of swot_anom_j
    meandrs_summary = meandrs_summary.reindex(reg_df.mon).reset_index(drop=True)

    # Insert values into dataframe
    reg_df.V_SWOT = swot_anom_j.V_SWOT
    reg_df.iloc[:, 3:] = meandrs_summary[:]

    # Write to file
    reg_df.to_csv(comp_fp, index=False)
    reg_list.append(reg_df)


# ******************************************************************************
# Aggregate SWOT and MeanDRS volume anomalies globally
# ******************************************************************************
print('Aggregating volume anomalies globally')
# MeanDRS global summary must be done separately from regional summaries
# to properly calculate standard deviations

# Sum all SWOT volume anomalies
swot_global_sum = sum([df.drop(columns=['dates'])
                       for df in swot_anom_all if not df.empty])

# Calculate SWOT global volume anomaly
comp_df.V_SWOT = swot_global_sum - np.mean(swot_global_sum)

# Sum all MeanDRS volume anomalies and identify months
meandrs_global_sum = sum([df.drop(columns=['dates'])
                          for df in meandrs_anom_all if not df.empty])
meandrs_global_sum.insert(0, 'mon',
                          pd.to_datetime(meandrs_anom_all[0].dates).dt.month)

# Summarize MeanDRS volume anomalies representing SWOT obs globally by month
global_summary = meandrs_global_sum.groupby('mon').agg({
    'mV_low_anom': ['mean', 'std'],
    'mV_nrm_anom': ['mean', 'std'],
    'mV_hig_anom': ['mean', 'std']})
global_summary.columns = ['_'.join(col).strip()
                          for col in global_summary.columns]

# Reorder to match months of swot_anom
global_summary = global_summary.reindex(comp_df.mon).reset_index(drop=True)

# Insert values into dataframe
comp_df.iloc[:, 3:] = global_summary[:]

# Write to file
comp_df.to_csv(comp_global_out, index=False)
