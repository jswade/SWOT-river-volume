#!/usr/bin/env python3
# ******************************************************************************
# swot_volume_FLaPE-Byrd.py
# ******************************************************************************
# Purpose:
# Estimate river volume globally from SWOT observations
# Author:
# Jeffrey Wade, 2024


# ******************************************************************************
# Import Python modules
# ******************************************************************************
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - swot_in
# 2 - V_out
# 3 - fit_out


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 4:
    print('ERROR - 3 arguments must be used')
    raise SystemExit(22)

swot_in = sys.argv[1]
V_out = sys.argv[2]
fit_out = sys.argv[3]


# ******************************************************************************
# Check if inputs exist
# ******************************************************************************
try:
    with open(swot_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + swot_in)
    raise SystemExit(22)


# ******************************************************************************
# Import FLaPE-Byrd ReachObservations function
# ******************************************************************************
print('Importing volume function')
# Check if the code is running in a script or interactive session
if '__file__' in globals():  # Running as a script
    script_dir = os.path.dirname(os.path.abspath(__file__))
else:
    script_dir = os.getcwd()

src_dir = os.path.abspath(os.path.join(script_dir, '.', 'src'))
sys.path.append(src_dir)
from FLaPE_Byrd_main_jw.ReachObservations_jw import ReachObservations


'''
Required inputs to ReachObservations class
D,RiverData,ConstrainHWSwitch=False,CalcAreaFitOpt=0,dAOpt=0,Verbose=False,σW=[]

D:
    nR = number of reaches
    xkm = reach midpoint distance downstream [m]
    L = reach lengths [m]
    nt = number of overpasses
    t = time [days]
    dt = time delta between successive overpasses [seconds]

RiverData:
    h = water surface elevation (wse) [m]
    h0 = wse at baseflow (minimum height?) [m]
    S = water surface slope [-]
    w = river width [m]
    sigh = wse uncertainty standard deviation [m]
    sigS = slope uncertainty standard deviation [-]
    sigW = width uncertainty standard deviation [m] (?)
    sigw = width uncertainty standard deviation [m]

ConstrainHWSwitch:
    True = Don't contrain?
    False = Constrain?

CalcAreaFitOpt:
    0 = don't calculate
    1 = use equal-spaced breakpoints
    2 = optimize breakpoints & fits together
    3 = optimize breakpoints, then optimize fits

dAOpt:
    0 = use MetroMan style calculation
    1 = use SWOT L2 style calculation

Verbose:
    True = enable printing
    False = disable printing

σW:
    empty = use sigW value
    values = use σW values

'''


# ******************************************************************************
# Set input class for FLaPE-Byrd ReachObservations
# ******************************************************************************
class Domain:
    def __init__(self, RiverData):
        self.nR = RiverData["nR"]  # number of reaches
        self.xkm = RiverData["xkm"]  # reach midpoint distance downstream [m]
        self.L = RiverData["L"]  # reach lengths, [m]
        self.nt = RiverData["nt"]  # number of overpasses
        self.t = RiverData["t"]  # time, [days]
        self.dt = RiverData["dt"]  # time between success. overpasses, [seconds]


# ******************************************************************************
# Load downloaded SWOT files
# ******************************************************************************
print('Loading files')
# ------------------------------------------------------------------------------
# Read processed csv files
# ------------------------------------------------------------------------------
# Read SWOT observation file
swot_df = pd.read_csv(swot_in)


# ******************************************************************************
# Perform volume computations for each region
# ******************************************************************************
print('Perform EIV fits')
# ------------------------------------------------------------------------------
# Filter SWOT observations
# ------------------------------------------------------------------------------
# Find original number of reaches
tot_rchs = np.unique(swot_df.reach_id)

# Remove observations with reach_q flags == 3
swot_df = swot_df[swot_df.reach_q < 3]

# Remove crossover cal != 0
swot_df = swot_df[swot_df.xovr_cal_q < 1]

# Remove dark frack > 0.3
swot_df = swot_df[swot_df.dark_frac < 0.3]

# Remove ice_clim > 0
swot_df = swot_df[swot_df.ice_clim_f == 0]

# Remove obs_frac_n (fraction of nodes in reach observed) <  0.5
swot_df = swot_df[swot_df.obs_frac_n > 0.5]

# Remove observations close to or far from nadir
swot_df = swot_df[((swot_df["xtrk_dist"] >= 10000) &
                   (swot_df["xtrk_dist"] <= 60000)) |
                  ((swot_df["xtrk_dist"] <= -10000) &
                   (swot_df["xtrk_dist"] >= -60000))]

# Remove non-Type 1 or 5 reaches
rch_type = swot_df.reach_id % 10
swot_df = swot_df[(rch_type == 1) | (rch_type == 5)]

# Drop rows where wse or width are negative
swot_df = swot_df[(swot_df['wse'] >= -1e5) & (swot_df['width'] >= -1e5)]

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

# Convert times to dates
swot_date = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').date() if '.' in x
             else datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()
             for x in swot_df.time]

# Retrieve unique date values from SWOT observations
date_obs = sorted(list(set(swot_date)))
date_obs = [x for x in date_obs if pd.notna(x)]

# Get unique mon-yrs
mon_yrs = sorted(list(set([datetime.strftime(x, '%y-%m') for
                           x in date_obs])))

# ------------------------------------------------------------------------------
# Prepare inputs to FLaPE-Byrd
# ------------------------------------------------------------------------------
# Create dataframe from list of SWOT observation dates
V_eiv = pd.DataFrame(np.full((len(rch_ids), len(date_obs)), np.nan),
                     columns=date_obs)

# Create dataframe to store fit parameters
fits_eiv = pd.DataFrame(np.full((len(rch_ids), 18), np.nan),
                        columns=['reach_id', 'fit_method', 'nobs',
                                 'med_flow_area', 'med_wse', 'med_width',
                                 'h_break_0', 'h_break_1', 'h_break_2',
                                 'h_break_3', 'm_1', 'm_2', 'm_3', 'y0_1',
                                 'y0_2', 'y0_3', 'ormse', 'mor'])
fits_eiv = fits_eiv.astype({
    'reach_id': 'Int64',
    'fit_method': 'string',
    'nobs': 'Int64',
    'med_flow_area': 'float64',
    'med_wse': 'float64',
    'med_width': 'float64',
    'h_break_0': 'float64',
    'h_break_1': 'float64',
    'h_break_2': 'float64',
    'h_break_3': 'float64',
    'm_1': 'float64',
    'm_2': 'float64',
    'm_3': 'float64',
    'y0_1': 'float64',
    'y0_2': 'float64',
    'y0_3': 'float64',
    'ormse': 'float64',
    'mor': 'float64'
})
fits_eiv.reach_id = rch_ids


# ------------------------------------------------------------------------------
# Compute EIV fits at each reach
# ------------------------------------------------------------------------------
for j in range(len(rch_ids)):

    print(j)

    # Select reach of interest
    rch_sel = rch_ids[j]

    # Retrieve reach length
    rch_ln = swot_df[swot_df.reach_id == rch_sel].p_length.values[0]

    # Filter dataframe to reach of interest
    swot_sel = swot_df[swot_df.reach_id == rch_sel]

    # Compute WSE variance
    hstd = np.std(swot_sel.wse)

    # Retrieve and format observation dates
    date_i = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f').date() if
              '.' in x
              else datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()
              for x in swot_sel.time]

    swot_sel.loc[:, 'time'] = [datetime.strptime(str(x),
                                                 '%Y-%m-%d %H:%M:%S.%f')
                               if '.' in str(x) else
                               datetime.strptime(str(x),
                                                 '%Y-%m-%d %H:%M:%S') +
                               timedelta(milliseconds=.1)
                               for x in swot_sel['time']]

    # Retrieve dates from swot_sel as days
    time_ind = pd.to_datetime(swot_sel.time.reset_index(drop=True))
    time_day = (time_ind - time_ind[0]).map(lambda x: x.total_seconds()
                                            / 86400) + 1

    # Retrieve time gap in seconds between observations
    time_diffs = np.diff(swot_sel.time)
    sec_between = np.array([td.total_seconds() for td in time_diffs])

    # Assemble ReachObservations inputs (Standard assumed uncertainty)
    ObsData = {'nR': 1,
               'xkm': np.array([0.]),
               'L': np.array(rch_ln),
               'nt': len(swot_sel),
               't': np.array(time_day),
               'dt': sec_between,
               'h': swot_sel.wse.values.reshape(1, len(swot_sel)),
               'h0': np.min(swot_sel.wse.values),
               'S': np.zeros(len(swot_sel)),
               'w': swot_sel.width.values.reshape(1, len(swot_sel)),
               'sigh': 0.1,
               'sigS': -9999.0,
               'sigW': [],
               'sigw': 30}

    # --------------------------------------------------------------------------
    # Run Errors-in-Variable
    # --------------------------------------------------------------------------
    # Run Domain and ReachObservations classes
    D = Domain(ObsData)
    obs = ReachObservations(D,  # Domain class
                            ObsData,  # Observation dictionary
                            ConstrainHWSwitch=True,  # Contrain HW Option
                            CalcAreaFitOpt=3,  # Optimize breakpoints + fits
                            dAOpt=1,  # SWOT L2 Style DA calculation
                            Verbose=False)  # Plotting option

    # Retrieve dA time series (m2)
    dA = pd.Series(obs.dA[0, :])

    # Set index of dA
    dA.index = pd.to_datetime(swot_sel.time)

    # Calculate delta V (del_A * reach length) (km3)
    dV = dA * rch_ln * 1e-9
    dV = dV.reset_index(drop=True)

    # Insert values into dataframe
    for k in range(len(date_i)):

        # Catch NaN time values
        if pd.isnull(date_i[k]):
            continue
        else:
            # Insert V value at location of date in V_eiv
            # If value is nan, insert value directly
            if np.isnan(V_eiv.loc[j, date_i[k]]):
                V_eiv.loc[j, date_i[k]] = dV[k]
            # If value already at date, take average of two values
            # This occurs when a reach is observed twice on the same day
            else:
                V_eiv.loc[j, date_i[k]] =\
                    np.mean([V_eiv.loc[j, date_i[k]], dV[k]])

    # Store fit parameters
    fits_eiv.loc[j, 'fit_method'] = obs.fit_method
    fits_eiv.loc[j, 'nobs'] = obs.area_fit['h_w_nobs'].item(0)
    fits_eiv.loc[j, 'med_flow_area'] = obs.area_fit['med_flow_area'].item(0)
    fits_eiv.loc[j, 'med_wse'] = np.median(obs.h)
    fits_eiv.loc[j, 'med_width'] = np.median(obs.w)
    fits_eiv.loc[j, 'h_break_0'] = obs.area_fit['h_break'].item(0)
    fits_eiv.loc[j, 'h_break_1'] = obs.area_fit['h_break'].item(1)
    fits_eiv.loc[j, 'h_break_2'] = obs.area_fit['h_break'].item(2)
    fits_eiv.loc[j, 'h_break_3'] = obs.area_fit['h_break'].item(3)
    fits_eiv.loc[j, 'm_1'] = obs.area_fit['fit_coeffs'].item(0)
    fits_eiv.loc[j, 'm_2'] = obs.area_fit['fit_coeffs'].item(1)
    fits_eiv.loc[j, 'm_3'] = obs.area_fit['fit_coeffs'].item(2)
    fits_eiv.loc[j, 'y0_1'] = obs.area_fit['fit_coeffs'].item(3)
    fits_eiv.loc[j, 'y0_2'] = obs.area_fit['fit_coeffs'].item(4)
    fits_eiv.loc[j, 'y0_3'] = obs.area_fit['fit_coeffs'].item(5)

    # Calculate mean orthogonal residual and orthogonal RMSE
    # Orthogonal residual is the euclidian distance between h,w and hhat,whhat
    orth_resid = np.sqrt((obs.hobs - obs.h)**2 + (obs.wobs - obs.w)**2)
    fits_eiv.loc[j, 'mor'] = np.mean(orth_resid)
    fits_eiv.loc[j, 'ormse'] = np.sqrt(np.mean(orth_resid**2))

    # # Optional Plots
    # # Plot observed Width vs WSE
    # plt.figure()
    # plt.scatter(swot_sel.wse, swot_sel.width)
    # plt.ylabel('Width, m')
    # plt.xlabel('WSE, m')

    # # Plot observed WSE vs dArea
    # plt.figure()
    # plt.scatter(swot_sel.wse, obs.dA[0, :], label='EIV')
    # plt.xlabel('WSE, m')
    # plt.ylabel('dA, m2')
    # plt.legend()

    # # Plot observed Width vs dArea
    # plt.figure()
    # plt.scatter(swot_sel.width, obs.dA[0, :], label='EIV')
    # plt.xlabel('Width, m')
    # plt.ylabel('dA, m2')
    # plt.legend()

    # # Plot dArea time series
    # plt.figure(figsize=(9.357, 2.255))
    # plt.plot(date_i, obs.dA[0, :], label='EIV', color='#ee762dff')
    # plt.scatter(date_i, obs.dA[0, :], label='EIV', color='#ee762dff')
    # plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    # plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.setp(plt.gca().get_xticklabels(), ha='right',
    #     rotation_mode='anchor')
    # plt.ylabel('dA, m2')
    # plt.ylim([-500, 1530])
    # ax = plt.gca()
    # ax.set_aspect(1/15)
    # plt.show()

    # # # Plot EIV height width regressions and constrained values
    # plt.figure()
    # for i in range(len(swot_sel)):
    #     plt.plot([obs.hobs[i], obs.h[0][i]],
    #              [obs.wobs[i], obs.w[0][i]],
    #              color='gray',  zorder=1)
    # for sd in range(3):
    #     htest = np.linspace(obs.area_fit['h_break'][sd],
    #                         obs.area_fit['h_break'][sd + 1], 10)
    #     wtest = obs.area_fit['fit_coeffs'][0, sd, 0] * htest +\
    #         obs.area_fit['fit_coeffs'][1, sd, 0]
    #     plt.plot(htest, wtest, c='#0078A3', zorder=2)
    # plt.scatter(obs.hobs, obs.wobs, c='black', zorder=3)
    # plt.scatter(obs.h, obs.w, c='#0078A3', zorder=3)
    # plt.xlabel('WSE, m')
    # plt.ylabel('Width, m')

    # # Plot dV time series
    # plt.figure(figsize=(9.357, 2.255))
    # plt.plot(date_i, dV, label='EIV', color='#0f355dff')
    # plt.scatter(date_i, dV, label='EIV', color='#0f355dff')
    # plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    # plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.setp(plt.gca().get_xticklabels(), ha='right',
    #     rotation_mode='anchor')
    # plt.ylabel('dV, m3')
    # ax = plt.gca()
    # plt.show()

    # # Plot combined dA and dV anomalies
    # fig, axes = plt.subplots(2, 1, figsize=(9.357, 4.5), sharex=True,
    #     gridspec_kw={'hspace': 0.3})
    # axes[0].plot(date_i, obs.dA[0, :], label='EIV', color='#ee762dff')
    # axes[0].scatter(date_i, obs.dA[0, :], label='EIV', color='#ee762dff')
    # axes[0].axhline(y=0, color='gray', linestyle='--', linewidth=1)
    # axes[0].set_ylabel('dA, m2')
    # axes[0].set_ylim([-500, 1530])
    # # axes[0].set_aspect(1 / 15)
    # axes[1].plot(date_i, dV, label='EIV', color='#0f355dff')
    # axes[1].scatter(date_i, dV, label='EIV', color='#0f355dff')
    # axes[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)
    # axes[1].set_ylabel('dV, km3')
    # axes[1].set_ylim([-0.01, 0.021])
    # axes[1].xaxis.set_major_locator(mdates.MonthLocator())
    # axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))
    # axes[1].tick_params(axis='x', rotation=45)
    # plt.setp(axes[1].get_xticklabels(), ha='right',
    #     rotation_mode='anchor')
    # plt.tight_layout()
    # plt.show()

# Write to file
V_eiv.index = rch_ids
V_eiv.to_csv(V_out, index=True)

fits_eiv.to_csv(fit_out, index=False)
