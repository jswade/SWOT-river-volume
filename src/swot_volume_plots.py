#!/usr/bin/env python3
# ******************************************************************************
# swot_volume_plots.py
# ******************************************************************************

# Purpose:
# Plot comparisons between SWOT and MeanDRS volumes.
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
import matplotlib.colors as mcolors
import geopandas as gpd
import cartopy.crs as ccrs


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - comp_reg_in
# 2 - comp_global_in
# 3 - scale_reg_in
# 4 - scale_global_in
# 5 - slice_reg_in
# 6 - slice_global_in
# 7 - mag_in
# 8 - corr_in
# 9 - world_in
# 10 - grat_in
# 11 - pfaf_in
# 12 - sword_anom_in
# 13 - num_obs_in


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 14:
    print('ERROR - 13 arguments must be used')
    raise SystemExit(22)

comp_reg_in = sys.argv[1]
comp_global_in = sys.argv[2]
scale_reg_in = sys.argv[3]
scale_global_in = sys.argv[4]
slice_reg_in = sys.argv[5]
slice_global_in = sys.argv[6]
mag_in = sys.argv[7]
corr_in = sys.argv[8]
world_in = sys.argv[9]
grat_in = sys.argv[10]
pfaf_in = sys.argv[11]
sword_anom_in = sys.argv[12]
num_obs_in = sys.argv[13]


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

try:
    if os.path.isdir(scale_reg_in):
        pass
except IOError:
    print('ERROR - '+scale_reg_in+' invalid folder path')
    raise SystemExit(22)

try:
    with open(scale_global_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + scale_global_in)
    raise SystemExit(22)

try:
    if os.path.isdir(slice_reg_in):
        pass
except IOError:
    print('ERROR - '+slice_reg_in+' invalid folder path')
    raise SystemExit(22)

try:
    with open(slice_global_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + slice_global_in)
    raise SystemExit(22)

try:
    with open(mag_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + mag_in)
    raise SystemExit(22)

try:
    with open(corr_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + corr_in)
    raise SystemExit(22)

try:
    with open(world_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + world_in)
    raise SystemExit(22)

try:
    with open(grat_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + grat_in)
    raise SystemExit(22)

try:
    with open(pfaf_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + pfaf_in)
    raise SystemExit(22)

try:
    if os.path.isdir(sword_anom_in):
        pass
except IOError:
    print('ERROR - '+sword_anom_in+' invalid folder path')
    raise SystemExit(22)

try:
    with open(num_obs_in) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + num_obs_in)
    raise SystemExit(22)


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
# Scaled SWOT Volumes
# ------------------------------------------------------------------------------
# Read regional scale files
scale_reg_files = sorted(list(glob.iglob(scale_reg_in + '*.csv')))
scale_reg_all = [pd.read_csv(x) for x in scale_reg_files]

# Read global scale file
scale_df = pd.read_csv(scale_global_in)

# ------------------------------------------------------------------------------
# SWOT MeanDRS Volume Slice Comparsions
# ------------------------------------------------------------------------------
# Read regional slice files
slice_reg_files = sorted(list(glob.iglob(slice_reg_in + '*.csv')))
slice_reg_all = [pd.read_csv(x) for x in slice_reg_files]

# Read global scale file
slice_df = pd.read_csv(slice_global_in)

# ------------------------------------------------------------------------------
# SWOT MeanDRS Volume Agreement Metrics
# ------------------------------------------------------------------------------
# Read agreemenet files
diff_mag_rat = pd.read_csv(mag_in)
diff_corr = pd.read_csv(corr_in)

# ------------------------------------------------------------------------------
# SWORD Anomaly Shapefiles
# ------------------------------------------------------------------------------
# Read regional SWORD anomaly files
sword_anom_files = sorted(list(glob.iglob(sword_anom_in + '*.shp')))

# Retrieve pfaf numbers from file
sw_pfaf_list = pd.Series([x.partition("pfaf_")[-1][0:2]
                          for x in sword_anom_files]).sort_values()

# Sort files by pfaf to align with SWOT observed files
sword_anom_files = pd.Series(sword_anom_files)[sw_pfaf_list.index.values].\
    tolist()

# Load SWORD files as shapefiles
sword_anom_all = [gpd.read_file(x) for x in sword_anom_files]

# ------------------------------------------------------------------------------
# Global Map Files
# ------------------------------------------------------------------------------
# Load basin polygon files
world = gpd.read_file(world_in)
grat = gpd.read_file(grat_in)
pfaf = gpd.read_file(pfaf_in)

# Reproject layers
pfaf = pfaf.to_crs("EPSG:4326")
world = world.to_crs("EPSG:4326")
grat = grat.to_crs("EPSG:4326")

# Sort pfaf region file by pfaf id
pfaf = pfaf.sort_values(by='PFAF_ID').reset_index(drop=True)

# ------------------------------------------------------------------------------
# Number of Observations
# ------------------------------------------------------------------------------
obs_df = pd.read_csv(num_obs_in)


# ******************************************************************************
# Create plots
# ******************************************************************************
print('Creating plots')
# ------------------------------------------------------------------------------
# Global SWOT Anomaly vs MeanDRS Mean Volume Anomaly
# ------------------------------------------------------------------------------
# Plot monthly means and standard deviation envelopes
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
plt.figure(figsize=(110/25.4, 90/25.4))
plt.plot(comp_df.mV_low_anom_mean, label='Low', color='#61742bff', zorder=6)
plt.fill_between(comp_df.index,
                 comp_df.mV_low_anom_mean - comp_df.mV_low_anom_std,
                 comp_df.mV_low_anom_mean + comp_df.mV_low_anom_std,
                 color='#e8f3cb', alpha=.7, label='Low Std', zorder=5)
plt.plot(comp_df.mV_nrm_anom_mean, label='Med', color='#2f6867', zorder=4)
plt.fill_between(comp_df.index,
                 comp_df.mV_nrm_anom_mean - comp_df.mV_nrm_anom_std,
                 comp_df.mV_nrm_anom_mean + comp_df.mV_nrm_anom_std,
                 color='#e2f2f2', alpha=.7, label='Med Std', zorder=3)
plt.plot(comp_df.mV_hig_anom_mean, label='Hig', color='#7549b3', zorder=2)
plt.fill_between(comp_df.index,
                 comp_df.mV_hig_anom_mean - comp_df.mV_hig_anom_std,
                 comp_df.mV_hig_anom_mean + comp_df.mV_hig_anom_std,
                 color='#e2d9ee', alpha=.7, label='Hig Std', zorder=1)
plt.plot(comp_df.V_SWOT, label='SWOT', color='black', zorder=7, linewidth=3)
plt.ylabel('River Storage Anomaly, km³', fontname='Arial', fontsize=12)
plt.legend(prop={'family': 'Arial', 'size': 12}, loc='upper left')
plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
comp_dates = pd.to_datetime(comp_df.dates).dt.strftime('%m-%y')
plt.xticks(ticks=range(0, 12), labels=comp_dates)
plt.xticks(ticks=range(len(comp_dates)), labels=comp_dates)
plt.xticks(rotation=45, fontname='Arial', fontsize=11)
plt.yticks(fontname='Arial', fontsize=11)
plt.tight_layout()
plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
plt.xlim([0, len(comp_dates) - 1])
plt.gca().set_frame_on(True)
plt.gca().spines['top'].set_zorder(10)
plt.gca().spines['right'].set_zorder(10)
plt.gca().spines['bottom'].set_zorder(10)
plt.gca().spines['left'].set_zorder(10)
plt.ylim([-1000, 1000])

# ------------------------------------------------------------------------------
# Regional SWOT Anomaly vs MeanDRS Mean Volume Anomaly
# ------------------------------------------------------------------------------
for i in range(len(comp_reg_all)):

    # Plot monthly means and standard deviation envelopes
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams['font.size'] = 12
    plt.figure()
    plt.plot(comp_reg_all[i].mV_low_anom_mean, label='Low',
             color='#61742bff', zorder=6)
    plt.fill_between(comp_reg_all[i].index,
                     comp_reg_all[i].mV_low_anom_mean -
                     comp_reg_all[i].mV_low_anom_std,
                     comp_reg_all[i].mV_low_anom_mean +
                     comp_reg_all[i].mV_low_anom_std,
                     color='#e8f3cb', alpha=.7, label='Low Std', zorder=5)
    plt.plot(comp_reg_all[i].mV_nrm_anom_mean, label='Med',
             color='#2f6867', zorder=4)
    plt.fill_between(comp_reg_all[i].index,
                     comp_reg_all[i].mV_nrm_anom_mean -
                     comp_reg_all[i].mV_nrm_anom_std,
                     comp_reg_all[i].mV_nrm_anom_mean +
                     comp_reg_all[i].mV_nrm_anom_std,
                     color='#e2f2f2', alpha=.7, label='Med Std', zorder=3)
    plt.plot(comp_reg_all[i].mV_hig_anom_mean, label='Hig',
             color='#7549b3', zorder=2)
    plt.fill_between(comp_reg_all[i].index,
                     comp_reg_all[i].mV_hig_anom_mean -
                     comp_reg_all[i].mV_hig_anom_std,
                     comp_reg_all[i].mV_hig_anom_mean +
                     comp_reg_all[i].mV_hig_anom_std,
                     color='#e2d9ee', alpha=.7,
                     label='Hig Std', zorder=1)
    plt.plot(comp_reg_all[i].V_SWOT, label='SWOT',
             color='black', zorder=7, linewidth=3)
    plt.ylabel('River Storage Anomaly, km³', fontname='Arial', fontsize=13)
    plt.title('SWOT vs MeanDRS RSA: Pfaf ' + pfaf_list[i])
    plt.legend(prop={'family': 'Arial', 'size': 12}, loc='upper left')
    plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
    comp_dates = pd.to_datetime(comp_reg_all[i].dates).dt.strftime('%m-%y')
    plt.xticks(ticks=range(0, 12), labels=comp_dates)
    plt.xticks(ticks=range(len(comp_dates)), labels=comp_dates)
    plt.xticks(rotation=45, fontname='Arial', fontsize=12)
    plt.yticks(fontname='Arial', fontsize=12)
    plt.tight_layout()
    plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
    plt.xlim([0, len(comp_dates) - 1])
    plt.gca().set_frame_on(True)
    plt.gca().spines['top'].set_zorder(10)
    plt.gca().spines['right'].set_zorder(10)
    plt.gca().spines['bottom'].set_zorder(10)
    plt.gca().spines['left'].set_zorder(10)

# ------------------------------------------------------------------------------
# Global Scaled SWOT Anomaly
# ------------------------------------------------------------------------------
# Plot scaled SWOT volume anomalies
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
plt.figure(figsize=(110/25.4, 90/25.4))
plt.plot(scale_df.V_SWOT, label='Observed SWOT RSA', color='black', linewidth=3,
         zorder=3)
plt.plot(scale_df.V_SWOT_ms, label='Scaled SWOT RSA',
         color='#c63741',
         linewidth=2,
         zorder=2)
plt.ylabel('River Storage Anomaly, km³', fontsize=12)
plt.legend()
plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
swot_dates_format = pd.to_datetime(scale_df.dates).dt.strftime('%m-%y')
plt.xticks(ticks=range(0, 12), labels=swot_dates_format)
plt.xticks(ticks=range(len(swot_dates_format)), labels=swot_dates_format)
plt.xlim([0, len(swot_dates_format) - 1])
# plt.ylim([-200, 200])
plt.xticks(rotation=45)
plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
plt.tight_layout()

# ------------------------------------------------------------------------------
# Regional Scaled SWOT Anomaly
# ------------------------------------------------------------------------------
for i in range(len(scale_reg_all)):

    # Plot scaled SWOT volume anomalies
    plt.figure()
    plt.plot(scale_reg_all[i].V_SWOT, label='SWOT', color='black', linewidth=3,
             zorder=3)
    plt.plot(scale_reg_all[i].V_SWOT_ms, label='SWOT (MERIT-SWORD)',
             color='#c63741',
             linewidth=2,
             zorder=2)
    plt.ylabel('River Storage Anomaly, km³', fontsize=13)
    plt.legend()
    plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
    swot_dates_format = pd.to_datetime(scale_reg_all[i].dates).\
        dt.strftime('%m-%y')
    plt.xticks(ticks=range(0, 12), labels=swot_dates_format)
    plt.xticks(ticks=range(len(swot_dates_format)), labels=swot_dates_format)
    plt.xlim([0, len(swot_dates_format) - 1])
    # plt.ylim([-200, 200])
    plt.xticks(rotation=45)
    plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
    plt.tight_layout()

# ------------------------------------------------------------------------------
# Global SWOT volume vs MeanDRS Yearly Slice Volume Anomaly
# ------------------------------------------------------------------------------
# MeanDRS Low Volume Scenario
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
plt.figure(figsize=(110/25.4, 90/25.4))
for j in range(60, 89):
    if j == 60:
        plt.plot(slice_df.index, slice_df.iloc[:, j],
                 color='#61742bff', alpha=0.2,
                 label='MeanDRS Annual Slice (Low)')
    else:
        plt.plot(slice_df.index, slice_df.iloc[:, j],
                 color='#61742bff', alpha=0.2)
plt.plot(slice_df.V_SWOT, label='SWOT', color='black', linewidth=2)
plt.ylabel('River Storage Anomaly, km³', fontsize=13)
plt.legend()
plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
plt.xticks(ticks=range(0, 12), labels=swot_dates_format)
plt.xticks(ticks=range(len(swot_dates_format)), labels=swot_dates_format)
plt.xticks(rotation=45)
plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
plt.xlim([0, len(slice_df.mon)-1])
plt.ylim([-1000, 1000])
plt.tight_layout()

# MeanDRS Normal Volume Scenario
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
plt.figure(figsize=(130/25.4, 90/25.4))
for j in range(31, 60):
    if j == 31:
        plt.plot(slice_df.index, slice_df.iloc[:, j],
                 color='#2f6867', alpha=0.2, label='MeanDRS Annual Slice (Med)')
    else:
        plt.plot(slice_df.index, slice_df.iloc[:, j],
                 color='#2f6867', alpha=0.2)
plt.plot(slice_df.V_SWOT, label='SWOT', color='black', linewidth=2)
plt.ylabel('River Storage Anomaly, km³', fontsize=13)
plt.legend(loc='lower right')
plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
plt.xticks(ticks=range(0, 12), labels=swot_dates_format)
plt.xticks(ticks=range(len(swot_dates_format)), labels=swot_dates_format)
plt.xticks(rotation=45)
plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
plt.xlim([0, len(slice_df.mon)-1])
plt.ylim([-1000, 1000])
plt.tight_layout()

# MeanDRS High Volume Scenario
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
plt.figure(figsize=(130/25.4, 90/25.4))
for j in range(2, 31):
    if j == 2:
        plt.plot(slice_df.index, slice_df.iloc[:, j],
                 color='#7549b3', alpha=0.2,
                 label='MeanDRS Annual Slice (High)')
    else:
        plt.plot(slice_df.index, slice_df.iloc[:, j],
                 color='#7549b3', alpha=0.2)
plt.plot(slice_df.V_SWOT, label='SWOT', color='black', linewidth=2)
plt.ylabel('River Storage Anomaly, km³', fontsize=13)
plt.legend()
plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
plt.xticks(ticks=range(0, 12), labels=swot_dates_format)
plt.xticks(ticks=range(len(swot_dates_format)), labels=swot_dates_format)
plt.xticks(rotation=45)
plt.setp(plt.gca().get_xticklabels(), ha='right', rotation_mode='anchor')
plt.xlim([0, len(slice_df.mon)-1])
plt.ylim([-1000, 1000])
plt.tight_layout()

# ------------------------------------------------------------------------------
# Regional SWOT volume vs MeanDRS Yearly Slice Volume Anomaly
# ------------------------------------------------------------------------------
for i in range(len(slice_reg_all)):

    # MeanDRS Low Volume Scenario
    plt.figure()
    for j in range(60, 89):
        plt.plot(slice_reg_all[i].index, slice_reg_all[i].iloc[:, j],
                 color='#61742bff', alpha=0.2)
    plt.plot(slice_reg_all[i].V_SWOT, label='SWOT', color='black', linewidth=2)
    plt.ylabel('River Storage Anomaly, km³', fontsize=13)
    plt.title('SWOT Vol vs Annual Slices of Low MeanDRS Pfaf ' + pfaf_list[i])
    plt.legend()
    plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
    plt.xticks(ticks=range(0, len(slice_reg_all[i].mon)),
               labels=pd.to_datetime(slice_reg_all[i].mon).dt.month)
    plt.xlim([0, len(slice_reg_all[i].mon)-1])
    plt.tight_layout()

    # MeanDRS Normal Volume Scenario
    plt.figure()
    for j in range(31, 60):
        plt.plot(slice_reg_all[i].index, slice_reg_all[i].iloc[:, j],
                 color='red', alpha=0.2)
    plt.plot(slice_reg_all[i].V_SWOT, label='SWOT', color='black', linewidth=2)
    plt.ylabel('River Storage Anomaly, km³', fontsize=13)
    plt.title('SWOT Vol vs Annual Slices of Med MeanDRS Pfaf ' + pfaf_list[i])
    plt.legend()
    plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
    plt.xticks(ticks=range(0, len(slice_reg_all[i].mon)),
               labels=pd.to_datetime(slice_reg_all[i].mon).dt.month)
    plt.xlim([0, len(slice_reg_all[i].mon)-1])
    plt.tight_layout()

    # MeanDRS High Volume Scenario
    plt.figure()
    for j in range(2, 31):
        plt.plot(slice_reg_all[i].index, slice_reg_all[i].iloc[:, j],
                 color='green', alpha=0.2)
    plt.plot(slice_reg_all[i].V_SWOT, label='SWOT', color='black', linewidth=2)
    plt.ylabel('River Storage Anomaly, km³', fontsize=13)
    plt.title('SWOT Vol vs Annual Slices of Hig MeanDRS Pfaf ' + pfaf_list[i])
    plt.legend()
    plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
    plt.xticks(ticks=range(0, len(slice_reg_all[i].mon)),
               labels=pd.to_datetime(slice_reg_all[i].mon).dt.month)
    plt.xlim([0, len(slice_reg_all[i].mon)-1])
    plt.tight_layout()


# ------------------------------------------------------------------------------
# Basin Volume Variability Magnitude
# ------------------------------------------------------------------------------
# Calculate basin variability magnitude based on scaled V_SWOT, set nan to 0
reg_V = pd.Series([np.nan_to_num(np.max(x.V_SWOT) - np.min(x.V_SWOT), nan=0)
                   for x in scale_reg_all])
reg_V_ms = pd.Series([np.nan_to_num(np.max(x.V_SWOT_ms) - np.min(x.V_SWOT_ms),
                                    nan=0)
                      for x in scale_reg_all])

# Duplicate value of Pfaf 35, as the Pfaf 35 is split by the anitmeridian
reg_V_dup = pd.concat([reg_V.iloc[:22], pd.Series([reg_V.iloc[21]]),
                       reg_V.iloc[22:]]).reset_index(drop=True)
reg_V_ms_dup = pd.concat([reg_V_ms.iloc[:22], pd.Series([reg_V_ms.iloc[21]]),
                          reg_V_ms.iloc[22:]]).reset_index(drop=True)

# Plot unscaled basin volume variability in Robinson projection
bins = np.array([0, 1, 5, 10, 25, 50, 75, 100, 150])
cmap = plt.get_cmap('Blues', len(bins))
colors = cmap(np.arange(cmap.N))
cust_cmap_obs = mcolors.ListedColormap(colors)
norm_obs = mcolors.BoundaryNorm(boundaries=bins, ncolors=cust_cmap_obs.N)

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
fig = plt.figure(figsize=(180/25.4, 115/25.4))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()
grat.plot(ax=ax, transform=ccrs.PlateCarree(), linewidth=0.2, color='gray',
          zorder=1)
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor="none",
           edgecolor="gray", linewidth=0.4, zorder=2, hatch=".")
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor='none',
           edgecolor="black", linewidth=0.4, zorder=3)
pfaf.plot(ax=ax, transform=ccrs.PlateCarree(), column=reg_V_dup,
          cmap=cust_cmap_obs,
          norm=norm_obs, zorder=3, edgecolor='black',
          linewidth=0.4)
sm = plt.cm.ScalarMappable(cmap=cust_cmap_obs, norm=norm_obs)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.67)
cbar.set_label('River Storage Variability, km³')
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{tick}' for tick in bins])
plt.show()

# Plot MERIT-SWORD scaled basin volume variability in Robinson projection
bins = np.array([0, 0.00001, 1, 5, 10, 25, 50, 100, 150, 200, 250])
cmap = plt.get_cmap('Reds', len(bins) - 1)
colors = cmap(np.arange(cmap.N))
colors[0] = [.5, .5, .5, 1]
cust_cmap_ms = mcolors.ListedColormap(colors)
norm_ms = mcolors.BoundaryNorm(boundaries=bins, ncolors=cust_cmap_ms.N)

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
fig = plt.figure(figsize=(180/25.4, 115/25.4))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()
grat.plot(ax=ax, transform=ccrs.PlateCarree(), linewidth=0.2, color='gray',
          zorder=1)
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor="none",
           edgecolor="gray", linewidth=0.4, zorder=2, hatch=".")
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor='none',
           edgecolor="black", linewidth=0.4, zorder=3)
pfaf.plot(ax=ax, transform=ccrs.PlateCarree(), column=reg_V_ms_dup,
          cmap=cust_cmap_ms,
          norm=norm_ms, zorder=3, edgecolor='black', linewidth=0.4)
sm = plt.cm.ScalarMappable(cmap=cust_cmap_ms, norm=norm_ms)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.67)
cbar.set_label('Scaled River Storage Variability, km³')
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{tick}' for tick in bins])
plt.show()

# ------------------------------------------------------------------------------
# Plot points/bars of ranked observed storage variability
# ------------------------------------------------------------------------------
# Format pfaf region names
pfaf_names = [str(x) for x in pfaf_list]

# Create dataframe of SWOT volumes
vol_df = pd.DataFrame({'pfaf_name': pfaf_list.astype('str'),
                       'V': reg_V,
                       'V_ms': reg_V_ms})

# Sort based on observed SWOT volume variability
vol_df = vol_df.sort_values(by="V", ascending=True).reset_index(drop='True')

# Plot bar plot of ranked storage variability
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 9
fig = plt.figure(figsize=(200/25.4, 90/25.4))
plt.bar(np.arange(len(vol_df)), vol_df.V_ms, width=0.6, color='#FF463B',
        edgecolor='black', label="SWOT (Scaled)", zorder=2)
plt.bar(np.arange(len(vol_df)), vol_df.V, width=0.6, color='#3FB9DE',
        edgecolor='black', label="SWOT (Observed)", zorder=3)
plt.xlim([-.5, 60.5])
plt.ylim([0, 250])
plt.ylabel("River Storage Variability, km³", fontsize=11)
plt.xlabel('Pfaf Region', fontsize=11)
plt.xticks(ticks=np.arange(len(vol_df)), labels=vol_df.pfaf_name, rotation=90)
plt.grid(axis='y', linestyle='--', linewidth=0.5, zorder=1)
plt.legend()
plt.show()

# ------------------------------------------------------------------------------
# Variability Magnitude Ratio SWOT vs MeanDRS Low
# ------------------------------------------------------------------------------
# Duplicate value of Pfaf 35, as the Pfaf 35 is split by the anitmeridian
mag_low_dup = pd.concat([diff_mag_rat.mag_rat_low[:22],
                         pd.Series([diff_mag_rat.mag_rat_low[21]]),
                        diff_mag_rat.mag_rat_low[22:]]).reset_index(drop=True)
mag_low_dup = mag_low_dup.fillna(-99)
pfaf['mag_low'] = mag_low_dup

# Plot variability magnitude ratio between SWOT volume and MeanDRS Low Volume
bins = np.array([-100, 0, 0.25, 0.5, 0.75, 1, 1.5, 2, 4, 20])
cmap = plt.get_cmap('coolwarm', len(bins) - 2)
colors = cmap(np.arange(cmap.N))
colors = colors[::-1]
colors = np.insert(colors, 0, np.array([0.5, 0.5, 0.5, 1]), axis=0)
cust_cmap_mag = mcolors.ListedColormap(colors)
norm_mag = mcolors.BoundaryNorm(boundaries=bins, ncolors=cust_cmap_mag.N)

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
fig = plt.figure(figsize=(180/25.4, 115/25.4))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()
grat.plot(ax=ax, transform=ccrs.PlateCarree(), linewidth=0.2, color='gray',
          zorder=1)
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor="none",
           edgecolor="gray", linewidth=0.4, zorder=2, hatch=".")
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor='none',
           edgecolor="black", linewidth=0.4, zorder=3)
pfaf.plot(ax=ax, transform=ccrs.PlateCarree(), column='mag_low',
          cmap=cust_cmap_mag, norm=norm_mag,
          zorder=3, edgecolor='black',
          linewidth=0.4)
sm = plt.cm.ScalarMappable(cmap=cust_cmap_mag, norm=norm_mag)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.67)
cbar.set_label('River Storage Variability Ratio')
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{tick:.2f}' for tick in bins])
plt.show()

# ------------------------------------------------------------------------------
# Variability Magnitude Ratio SWOT/MeanDRS, Best Scenario
# ------------------------------------------------------------------------------
# Duplicate value of Pfaf 35, as the Pfaf 35 is split by the anitmeridian
mag_best_scen = pd.concat([diff_mag_rat.best_scen[:22],
                           pd.Series([diff_mag_rat.best_scen[21]]),
                           diff_mag_rat.best_scen[22:]]).reset_index(drop=True)
mag_best_scen = mag_best_scen.fillna('NA')
pfaf['mag_best_scen'] = mag_best_scen

# Plot closest matching MeanDRS scenario to SWOT based on Magnitude Ratio
scen_cats = ['NA', 'low', 'nrm', 'hig']
scen_colors = ['gray', '#BADB62', '#92CECE', '#B59FD4']

cat_to_int = {cat: i for i, cat in enumerate(scen_cats)}
pfaf['mag_best_scen_code'] = pfaf['mag_best_scen'].map(cat_to_int)

cust_cmap_mag_scen = mcolors.ListedColormap(scen_colors)
boundaries = np.arange(len(scen_cats) + 1) - 0.5  # center the ticks
norm_mag_scen = mcolors.BoundaryNorm(boundaries, len(scen_cats))

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
fig = plt.figure(figsize=(180/25.4, 115/25.4))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()
grat.plot(ax=ax, transform=ccrs.PlateCarree(), linewidth=0.2, color='gray',
          zorder=1)
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor="none",
           edgecolor="gray", linewidth=0.4, zorder=2, hatch=".")
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor='none',
           edgecolor="black", linewidth=0.4, zorder=3)
pfaf.plot(ax=ax, transform=ccrs.PlateCarree(),
          column='mag_best_scen_code',
          cmap=cust_cmap_mag_scen, norm=norm_mag_scen,
          edgecolor='black', linewidth=0.4, zorder=3)
plt.show()

# ------------------------------------------------------------------------------
# Correlation with No Lag SWOT vs MeanDR
# ------------------------------------------------------------------------------
# Duplicate value of Pfaf 35, as the Pfaf 35 is split by the anitmeridian
corr_dup = pd.concat([diff_corr.corr_0[:22],
                      pd.Series([diff_corr.corr_0[21]]),
                      diff_corr.corr_0[22:]]).reset_index(drop=True)
corr_dup = corr_dup.fillna(-99).astype(float)
pfaf['corr_dup'] = corr_dup

# Plot no lag correlation between SWOT volume and MeanDRS Volume
bins = np.array([-100, -1, -.8, -.6, -.4, -.2, 0, .2, .4, .6, .8, 1])
cmap = plt.get_cmap('coolwarm', len(bins) - 2)
colors = cmap(np.arange(cmap.N))
colors = colors[::-1]
colors = np.insert(colors, 0, np.array([0.5, 0.5, 0.5, 1]), axis=0)
cust_cmap_corr = mcolors.ListedColormap(colors)
norm_corr = mcolors.BoundaryNorm(boundaries=bins, ncolors=cust_cmap_corr.N)

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
fig = plt.figure(figsize=(180/25.4, 115/25.4))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()
grat.plot(ax=ax, transform=ccrs.PlateCarree(), linewidth=0.2, color='gray',
          zorder=1)
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor="none",
           edgecolor="gray", linewidth=0.4, zorder=2, hatch=".")
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor='none',
           edgecolor="black", linewidth=0.4, zorder=3)
pfaf.plot(ax=ax, transform=ccrs.PlateCarree(), column='corr_dup',
          cmap=cust_cmap_corr, norm=norm_corr,
          zorder=3, edgecolor='black',
          linewidth=0.4)
sm = plt.cm.ScalarMappable(cmap=cust_cmap_corr, norm=norm_corr)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.67)
cbar.set_label('River Storage Anomaly \nPearson Correlation',)
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{tick:.1f}' for tick in bins])
plt.show()

# ------------------------------------------------------------------------------
# Best Lag Correlation with SWOT vs MeanDR
# ------------------------------------------------------------------------------
# Duplicate value of Pfaf 35, as the Pfaf 35 is split by the anitmeridian
corr_best_lag = pd.concat([diff_corr.best_lag[:22],
                           pd.Series([diff_corr.best_lag[21]]),
                           diff_corr.best_lag[22:]]).reset_index(drop=True)
corr_best_lag = corr_best_lag.fillna(-99).astype(float)
abs_best_lag = np.abs(corr_best_lag)
abs_best_lag[abs_best_lag == 99] = -99
pfaf['abs_best_lag'] = np.abs(corr_best_lag)

# Plot no lag correlation between SWOT volume and MeanDRS Volume
bins = np.array([-900, -.5, .5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
cmap = plt.get_cmap('Blues', len(bins) - 2)
colors = cmap(np.arange(cmap.N))
colors = colors[::-1]
colors = np.insert(colors, 0, np.array([0.5, 0.5, 0.5, 1]), axis=0)
cust_cmap_lag = mcolors.ListedColormap(colors)
norm_lag = mcolors.BoundaryNorm(boundaries=bins, ncolors=cust_cmap_lag.N)

plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 11
fig = plt.figure(figsize=(180/25.4, 115/25.4))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_global()
grat.plot(ax=ax, transform=ccrs.PlateCarree(), linewidth=0.2, color='gray',
          zorder=1)
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor="none",
           edgecolor="gray", linewidth=0.4, zorder=2, hatch=".")
world.plot(ax=ax, transform=ccrs.PlateCarree(), facecolor='none',
           edgecolor="black", linewidth=0.4, zorder=3)
pfaf.plot(ax=ax, transform=ccrs.PlateCarree(), column='abs_best_lag',
          cmap=cust_cmap_lag, norm=norm_lag,
          zorder=3, edgecolor='black',
          linewidth=0.4)
sm = plt.cm.ScalarMappable(cmap=cust_cmap_lag, norm=norm_lag)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.67)
cbar.set_label('River Storage Anomaly \nOptimal Absolute Lag, months')
cbar.set_ticks(bins)
cbar.set_ticklabels([f'{tick:.2f}' for tick in bins])
plt.show()

# ------------------------------------------------------------------------------
# Number of Observations by region
# ------------------------------------------------------------------------------
# Plot bar plot of number of reaches observed
plt.rcParams["font.family"] = "Arial"
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams['font.size'] = 9
fig = plt.figure(figsize=(200/25.4, 90/25.4))
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
plt.ylabel('Number of Reaches', fontsize=11)
plt.xlabel('Pfaf Region', fontsize=11)
plt.xticks(ticks=np.arange(len(obs_df)), labels=obs_df.pfaf, rotation=90)
plt.legend()
plt.show()
