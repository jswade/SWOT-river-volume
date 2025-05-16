#!/usr/bin/env python3
# ******************************************************************************
# tst_cmp.py
# ******************************************************************************

# Purpose:
# Given an original file and a file generating during testing,
# ensure that files are identical.

# Author:
# Jeffrey Wade, 2025


# ******************************************************************************
# Import Python modules
# ******************************************************************************
import sys
import filecmp
import pathlib


# ******************************************************************************
# Declaration of variables (given as command line arguments)
# ******************************************************************************
# 1 - file_org
# 2 - file_tst


# ******************************************************************************
# Define comparison functions
# ******************************************************************************
# Identify type of file for comparison
def compare_files(file_org, file_tst):
    suffix = pathlib.Path(file_org).suffix.lower()

    if suffix == '.shp':
        return compare_shapefiles(file_org, file_tst)
    elif suffix == '.csv':
        return compare_csvs(file_org, file_tst)
    elif suffix == '.tif':
        return compare_tifs(file_org, file_tst)
    else:
        return filecmp.cmp(file_org, file_tst, shallow=False)


# Compare original and testing shapefiles with tolerance
def compare_shapefiles(file_org, file_tst):
    import geopandas as gpd
    import pandas as pd

    try:
        gdf1 = gpd.read_file(file_org)
        gdf2 = gpd.read_file(file_tst)

        # Compare lengths
        if len(gdf1) != len(gdf2):
            print(f"Mismatch in number of features: {len(gdf1)} vs {len(gdf2)}")
            return False

        # Compare column names
        if set(gdf1.columns) != set(gdf2.columns):
            print("Mismatch in column names:")
            print("Original:", sorted(gdf1.columns))
            print("Test:    ", sorted(gdf2.columns))
            return False

        # Reorder columns to match
        gdf2 = gdf2[gdf1.columns]

        # Sort by index
        gdf1 = gdf1.sort_index().reset_index(drop=True)
        gdf2 = gdf2.sort_index().reset_index(drop=True)

        # Compare geometries with tolerance
        g1_geom = gdf1.geometry.reset_index(drop=True)
        g2_geom = gdf2.geometry.reset_index(drop=True)

        # Identify geometry mismatches
        mismatches = []
        for i in range(len(g1_geom)):
            if not g1_geom.iloc[i].equals_exact(g2_geom.iloc[i],
                                                tolerance=1e-6):
                mismatches.append(i)
        if mismatches:
            print(f"Geometry mismatch in {len(mismatches)} "
                  "rows: {mismatches[:10]}... [truncated]")
            return False

        # Check attribute equality
        df1 = gdf1.drop(columns="geometry")
        df2 = gdf2.drop(columns="geometry")
        if not df1.equals(df2):
            diff_mask = ~(df1 == df2).all(axis=1)
            print("Attribute mismatch in rows:", list(df1.index[diff_mask]))
            print("Differences (first few rows):")
            print(pd.concat([df1[diff_mask], df2[diff_mask]], axis=1,
                            keys=['Original', 'Test']).head())
            return False

        return True

    except Exception as e:
        print("ERROR comparing shapefiles:", e)
        return False


# Compare original and testing csv files
def compare_csvs(file_org, file_tst):
    import pandas as pd
    try:
        df1 = pd.read_csv(file_org).sort_index(axis=1)
        df2 = pd.read_csv(file_tst).sort_index(axis=1)
        return df1.equals(df2)
    except Exception as e:
        print("ERROR comparing CSVs:", e)
        return False


# Compare original and testing tif files
def compare_tifs(file_org, file_tst):
    import rasterio
    import numpy as np
    try:
        with rasterio.open(file_org) as src1, rasterio.open(file_tst) as src2:
            if src1.count != src2.count or src1.shape != src2.shape:
                return False
            for i in range(1, src1.count + 1):
                if not np.allclose(src1.read(i), src2.read(i), equal_nan=True):
                    return False
            return True
    except Exception as e:
        print("ERROR comparing TIFFs:", e)
        return False


# ******************************************************************************
# Get command line arguments
# ******************************************************************************
IS_arg = len(sys.argv)
if IS_arg != 3:
    print('ERROR - 2 arguments must be used')
    raise SystemExit(22)

file_org = sys.argv[1]
file_tst = sys.argv[2]


# ******************************************************************************
# Check if files exist
# ******************************************************************************
try:
    with open(file_org) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + file_org)
    raise SystemExit(22)

try:
    with open(file_tst) as file:
        pass
except IOError:
    print('ERROR - Unable to open ' + file_tst)
    raise SystemExit(22)


# ******************************************************************************
# Compare original and test files
# ******************************************************************************
# Perform comparison
if not compare_files(file_org, file_tst):
    print('ERROR - Comparison failed.')
    raise SystemExit(99)
else:
    print('Comparison successful!')
