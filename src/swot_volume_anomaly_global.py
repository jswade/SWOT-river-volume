#!/usr/bin/env python3
# ******************************************************************************
# swot_volume_anomaly_global.py
# ******************************************************************************

# Purpose:
# Calculate the volume anomaly at each SWOT reach
# Author:
# Jeffrey Wade, 2024

# ******************************************************************************
# Import Python modules
# ******************************************************************************
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ******************************************************************************
# Set input file paths
# ******************************************************************************
# # Set volume file path
# V_in = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/V_EIV/'\
#     'swot_vol_pfaf_11_2023-10-01_2024-09-30.csv'

# # Set SWOT observation input
# swot_in = '/Users/jwade/jpl/computing/swot_volume/input/SWOT/global_obs/'\
#     'swot_pfaf_11_2023-10-01_2024-09-30.csv'

# # Set volume anomaly output files
# V_anom_out = '/Users/jwade/jpl/computing/swot_volume/output/SWOT/V_anom/'\
#     'V_anom_pfaf_11_2023-10-01_2024-09-30.csv'


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - V_in
# 2 - swot_in
# 3 - ms_in
# 4 - V_anom_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 4:
    print('ERROR - 3 arguments must be used')
    raise SystemExit(22)

V_in = sys.argv[1]
swot_in = sys.argv[2]
V_anom_out = sys.argv[3]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    with open(V_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + V_in)
    raise SystemExit(22)

try:
    with open(swot_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + swot_in)
    raise SystemExit(22)


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# Read V anomaly files
V_eiv = pd.read_csv(V_in)

# Set reach_id as index
V_eiv = V_eiv.set_index("reach_id", drop=True)

# Convert columns to dates
V_eiv.columns = pd.to_datetime(V_eiv.columns, utc=True).date

# Read SWOT observation file
swot_df = pd.read_csv(swot_in)


# ******************************************************************************
# Calculate SWOT anomalies at each reach, interpolating to filtered times
# ******************************************************************************
print('Computing volume anomalies')
# ------------------------------------------------------------------------------
# Identify SWOT observations removed by filtering
# ------------------------------------------------------------------------------
# If unfiltered times are past the desired end time, change to end time
end_time = pd.to_datetime("2024-09-30 23:59:59", utc=True)
swot_df['time'] = pd.to_datetime(swot_df.time, format='ISO8601', utc=True)
swot_df.loc[swot_df['time'] > end_time, 'time'] = end_time

# Convert times to dates
swot_df['dates'] = swot_df['time'].dt.date

# Make copy of unfiltered swot_df
swot_df_full = swot_df.copy()

# Remove observations with reach_q flags == 3
swot_df = swot_df[swot_df.reach_q < 3]

# Remove crossover cal != 0
swot_df = swot_df[swot_df.xovr_cal_q < 1]

# Remove dark frack > 0.3
swot_df = swot_df[swot_df.dark_frac < 0.3]

# Remove ice_clim > 0
swot_df = swot_df[swot_df.ice_clim_f == 0]

# Remove obs_frac_n (fraction of nodes in reach observed) < 0.5
swot_df = swot_df[swot_df.obs_frac_n > 0.5]

# Remove observations close to or far from nadir
swot_df = swot_df[((swot_df["xtrk_dist"] >= 10000) &
                   (swot_df["xtrk_dist"] <= 60000)) |
                  ((swot_df["xtrk_dist"] <= -10000) &
                   (swot_df["xtrk_dist"] >= -60000))]

# Drop rows where wse or width are negative
swot_df = swot_df[(swot_df['wse'] >= -1e5) & (swot_df['width'] >= -1e5)]

# Remove non-Type 1/5 reaches
rch_type = swot_df.reach_id % 10
swot_df = swot_df[(rch_type == 1) | (rch_type == 5)]

# Find number of observations for each reach
rch_counts = swot_df.reach_id.value_counts()

# Retrieve reaches with >= 5 observations
rch_ids = rch_counts.index[rch_counts >= 5]

# Identify reaches where WSE range is abnormally high
rch_remove = []
for j in range(len(rch_ids)):

    # Filter dataframe to reach of interest
    swot_sel = swot_df[swot_df.reach_id == rch_ids[j]]

    # If WSE range larger than reasonable threshold, remove reach
    if swot_sel.wse.max() - swot_sel.wse.min() > 20:
        rch_remove.append(rch_ids[j])

# Drop rch_remove reachs from rch_ids
rch_ids = rch_ids[~np.isin(rch_ids, rch_remove)]

# Retrieve unfiltered dates  for each SWOT observed reach
date_obs_unfil = []
for i in range(len(rch_ids)):
    date_obs_unfil.append(swot_df_full.dates[swot_df_full.reach_id ==
                                             rch_ids[i]])

# Retrieve unique date values from SWOT observations
date_uniq = sorted(list(set(swot_df_full.dates)))
date_uniq = [x for x in date_uniq if pd.notna(x)]

# Get unique mon-yrs
mon_yrs = sorted(list(set([datetime.strftime(x, '%y-%m') for x in
                           date_uniq])))

# Create list of dates between first and last swot_date
if len(date_uniq) != 0:
    date_list = [date_uniq[0] + timedelta(days=x) for
                 x in range((date_uniq[-1] - date_uniq[0]).days + 1)]
else:
    date_list = []

# ------------------------------------------------------------------------------
# Calculate volume anomalies at each reach
# ------------------------------------------------------------------------------
# Create dataframe to store volume anomalies
V_a_interp_df = pd.DataFrame(np.full((len(rch_ids), len(date_list)),
                                     np.nan),
                             index=rch_ids, columns=date_list)

# Loop through SWOT reaches
for i in range(len(rch_ids)):

    # Select reach
    rch_i = rch_ids[i]

    # Retrieve volume values of filtered SWOT observations
    V_i = V_eiv.loc[rch_i].dropna()

    # Interpolate values at dates of unfiltered observations
    V_i_reind = V_i.reindex(pd.to_datetime(V_i.
                                           index.union(date_obs_unfil[i])))
    V_i_interp = V_i_reind.interpolate(method='time')
    V_i_interp = V_i_interp.ffill().bfill()

    # Calculate volume anomaly (V - V_mean)
    V_a_interp = V_i_interp - np.mean(V_i_interp)

    # Reindex V_a to date and calculate mean for duplicate dates
    V_a_interp.index = V_a_interp.index.map(lambda x: x.date())
    V_a_interp = V_a_interp.groupby(V_a_interp.index).mean()

    # Insert into dataframe
    V_a_interp_df.loc[rch_i, V_a_interp.index] = V_a_interp

# Calculate monthly volume anomalies
V_a_interp_df.columns = pd.to_datetime(V_a_interp_df.columns)
V_a_interp_mon_df = V_a_interp_df.T.resample('ME').mean().T

# Convert columns to "YYYY-MM" format
V_a_interp_mon_df.columns = V_a_interp_mon_df.columns.strftime('%Y-%m')

# Write to file
V_a_interp_mon_df.to_csv(V_anom_out)
