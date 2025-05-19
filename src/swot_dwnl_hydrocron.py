#!/usr/bin/env python3
# ******************************************************************************
# swot_dwnl_hydrocron
# ******************************************************************************
# Purpose:
# Download SWOT L2 HR River Data Products using Hydrocron
# Author:
# Jeffrey Wade, 2024

# ******************************************************************************
# Import Python modules
# ******************************************************************************
import sys
import requests
import io
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import geopandas as gpd
import earthaccess


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - sword_in
# 2 - date1
# 3 - date2
# 4 - swot_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 5:
    print('ERROR - 4 arguments must be used')
    raise SystemExit(22)

sword_in = sys.argv[1]
date1 = sys.argv[2]
date2 = sys.argv[3]
swot_out = sys.argv[4]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    with open(sword_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + sword_in)
    raise SystemExit(22)


# ******************************************************************************
# Earthdata Authentication
# ******************************************************************************
earthaccess.login()


# ******************************************************************************
# Read files
# ******************************************************************************
print('Reading files')
# ------------------------------------------------------------------------------
# SWORD reach file
# ------------------------------------------------------------------------------
# Load sword reach file
sword_i = gpd.read_file(sword_in, crs="EPSG:4326")

# Retrieve pfaf numbers from file
pfaf_num = sword_in.partition("reaches_hb")[-1][0:2]


# ******************************************************************************
# Make API call to Hydrocron for each pfaf region and reach
# ******************************************************************************
print('Making API calls to Hydrocron')
# Set variables of interest
swot_vars = 'reach_id,time,wse,wse_u,wse_r_u,width,width_u,'\
    'reach_q,reach_q_b,dark_frac,ice_clim_f,ice_dyn_f,xtrk_dist,'\
    'obs_frac_n,xovr_cal_q,p_length,crid'

# Define base date
base_date = datetime(2000, 1, 1)

# Read reach ids
rch_id = sword_i.reach_id

# Remove ghost reaches (type 6)
rch_type = np.array([x % 10 for x in rch_id])
rch_id = rch_id[rch_type != 6]

# Create API calls
api_calls = ['https://soto.podaac.earthdatacloud.nasa.gov/hydrocron/v1/'
             'timeseries?feature=Reach&feature_id=' + str(x) +
             '&output=csv&start_time=' + date1 + 'T00:00:00Z&'
             'end_time=' + date2 + 'T23:59:59Z&fields=' + swot_vars
             for x in rch_id]

# Initialize dataframe
swot_df = None

# Loop through api_calls
for j in range(len(api_calls)):

    # print(j)

    # Make API call
    response = requests.get(api_calls[j]).json()

    # Check request status, catching errors in api call
    if 'error' in response:
        print('Error:', response['error'])
    else:
        try:
            if response['status'] == '200 OK':

                # Retrieve csv string
                csv_str = response['results']['csv']

                # Convert to dataframe
                df = pd.read_csv(io.StringIO(csv_str))

                # Drop rows with negative times
                df = df[df['time'] >= 0]

                # If df has no valid observations, skip to next reach
                if len(df) == 0:
                    continue

                # Drop all unit columns
                df = df[df.columns.drop(list(df.filter(like='units')))]

                # Convert times
                df['time'] = df['time'].apply(lambda x: base_date +
                                              timedelta(seconds=x))

                # For first file, start new dataframe
                if swot_df is None:
                    swot_df = df.copy()
                # For subsequent files, append to dataframe
                else:
                    swot_df = pd.concat([swot_df, df], ignore_index=True)

            # Catch other errors
            else:
                print('Error:', response['response'])

        except KeyError as e:
            print(f"KeyError: {e}. The status key does not exist.")

# Write to file if region has valid observations
if swot_df is not None:
    swot_df.to_csv(swot_out, index=False)
# Otherwise, write empty dataframe
else:
    swot_df = pd.DataFrame(columns=swot_vars.split(','))
    swot_df.to_csv(swot_out, index=False)
