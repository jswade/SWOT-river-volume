#!/usr/bin/env python3
# ******************************************************************************
# meandrs_volume_agreement.py
# ******************************************************************************

# Purpose:
# Assess the agreement between SWOT and MeanDRS volumes.
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
from scipy.signal import correlate


# # ******************************************************************************
# # Set input file paths
# # ******************************************************************************
# # Set input file path for volume anomalies
# comp_reg_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/'\
#     'global_summary/MeanDRS_comp/regional/'

# comp_global_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/'\
#     'global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv'

# mag_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/global_summary/'\
#     'MeanDRS_agree/MeanDRS_agree_global_mag_ratio.csv'

# corr_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/global_summary/'\
#     'MeanDRS_agree/MeanDRS_agree_global_corr.csv'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - comp_reg_in
# 2 - comp_global_in
# 3 - mag_out
# 4 - corr_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 3:
    print('ERROR - 2 arguments must be used')
    raise SystemExit(22)

comp_reg_in = sys.argv[1]
comp_global_in = sys.argv[2]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    if os.path.isdir(comp_reg_in):
        pass
except IOError:
    print('ERROR - '+comp_reg_in+' invalid folder path')
    raise SystemExit(22)

try:
    with open(comp_global_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + comp_global_in)
    raise SystemExit(22)


# ******************************************************************************
# Define functions
# ******************************************************************************
# Define function to assess optimum cross correlation with lag
def cross_corr(x, y):
    corr = correlate(y - np.mean(y), x - np.mean(x), mode='full')
    lags = np.arange(-len(x) + 1, len(x))
    max_corr = np.max(corr)
    best_lag = lags[np.argmax(corr)]
    return max_corr, best_lag


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# SWOT MeanDRS Volume Mean Comparisons
# ------------------------------------------------------------------------------
# Read regional comparison files
comp_reg_files = sorted(list(glob.iglob(comp_reg_in + '*.csv')))
comp_reg_all = [pd.read_csv(x) for x in comp_reg_files]

# Retrieve pfaf regions of files
pfaf_list = pd.Series([x.partition("pfaf_")[-1][0:2] for x in comp_reg_files])

# Read global comparison file
comp_df = pd.read_csv(comp_global_in)

# ------------------------------------------------------------------------------
# Assess agreement of annual magnitude of volume variability
# ------------------------------------------------------------------------------
diff_mag = pd.DataFrame(index=range(len(pfaf_list)),
                        columns=['pfaf', 'mag_rat_low', 'mag_rat_nrm',
                                 'mag_rat_hig', 'best_scen'])
diff_mag.pfaf = pfaf_list

for i in range(len(comp_reg_all)):

    # Calculate volume annual magnitude of variability (km3)
    comp_reg_i = comp_reg_all[i]
    comp_reg_mag = comp_reg_i.iloc[:, 2:].max() - comp_reg_i.iloc[:, 2:].min()

    # If all SWOT values are 0, leave as nan
    if (comp_reg_i.V_SWOT == 0).all() | \
       (comp_reg_i.mV_low_anom_mean == 0).all():
        continue

    # Calculate ratio of volume annual range: SWOT/MeanDRS Low Volume
    diff_mag.loc[i, 'mag_rat_low'] = comp_reg_mag.V_SWOT /\
        comp_reg_mag.mV_low_anom_mean

    # Calculate ratio of volume annual range: SWOT/MeanDRS Nrm Volume
    diff_mag.loc[i, 'mag_rat_nrm'] = comp_reg_mag.V_SWOT /\
        comp_reg_mag.mV_nrm_anom_mean

    # Calculate ratio of volume annual range: SWOT/MeanDRS Hig Volume
    diff_mag.loc[i, 'mag_rat_hig'] = comp_reg_mag.V_SWOT /\
        comp_reg_mag.mV_hig_anom_mean

    # Identify MeanDRS scenario with best agreement
    diff_mag.loc[i, 'best_scen'] = min(('low', 'nrm', 'hig'), key=lambda x:
                                       abs(diff_mag.loc[i, f'mag_rat_{x}'] - 1))

# Write to file
diff_mag.to_csv(mag_out, index=False)

# ------------------------------------------------------------------------------
# Assess agreement of timing of time series
# ------------------------------------------------------------------------------
diff_corr = pd.DataFrame(index=range(len(pfaf_list)),
                         columns=['pfaf', 'corr_neg5', 'corr_neg4', 'corr_neg3',
                                  'corr_neg2', 'corr_neg1', 'corr_0',
                                  'corr_pos1', 'corr_pos2', 'corr_pos3',
                                  'corr_pos4', 'corr_pos5', 'corr_pos6',
                                  'best_lag'])
diff_corr.pfaf = pfaf_list


# Define function for circular cross correlation, where y is rotated around x
# Calculate Pearson correlation at each shift
def circ_cross_corr(x, y):
    corrs = []
    # Define lag shifts, with 0 being original alignment
    lag = [0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1]
    x = comp_reg_i.V_SWOT
    y = comp_reg_i.mV_low_anom_mean
    for i in range(len(x)):
        y_shift = np.roll(y, i)
        corr = np.corrcoef(x, y_shift)[0, 1]
        corrs.append(corr)
    corrs_sr = pd.Series(corrs, index=lag).sort_index()
    return corrs_sr


for i in range(len(comp_reg_all)):

    comp_reg_i = comp_reg_all[i]

    # If all SWOT values are 0, leave as nan
    if (comp_reg_i.V_SWOT == 0).all() | \
       (comp_reg_i.mV_low_anom_mean == 0).all():
        continue

    # Calculate lagged cross-correlation of SWOT and MeanDRS Low Volume anoms
    # Cross correlations are same for all MeanDRS scenarios (scalar multp.)
    diff_corr.iloc[i, 1:13] = circ_cross_corr(comp_reg_i.V_SWOT,
                                              comp_reg_i.mV_low_anom_mean)

# Find best lag correlation for each region
diff_corr.loc[:, 'best_lag'] = diff_corr.iloc[:, 1:13].apply(
    lambda row: row.idxmax(skipna=True) if row.notna().any() else np.nan,
    axis=1)

# Reformat lags
lags = diff_corr['best_lag'].str.replace('corr_', '', regex=False)

diff_corr['best_lag'] = \
    (lags.where(lags == '0', None)
     .fillna(lags.where(lags.str.startswith('pos')).str[3:].astype(float))
     .fillna(lags.where(lags.str.startswith('neg')).str[3:].astype(float).
             mul(-1)))

# Write to file
diff_corr.to_csv(corr_out, index=False)
