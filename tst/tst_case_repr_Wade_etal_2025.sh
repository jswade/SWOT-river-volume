#!/bin/bash
#*****************************************************************************
#tst_case_repr_Wade_etal_2025.sh
#*****************************************************************************
#Purpose:
#This script reproduces testing pre- and post-processing steps used in the
#writing of:

#DOI: xx.xxxx/xxxxxxxxxxxx

#Zenodo
#DOI: XXXXX
#The following are the possible arguments:
# - No argument: all unit tests are run
# - One unique unit test number: this test is run
# - Two unit test numbers: all tests between those (included) are run
#The script returns the following exit codes
# - 0  if all downloads are successful
# - 22 if there was a conversion problem
# - 44 if one download is not successful
#Author:
#Jeffrey Wade, Cedric H. David, 2025.

#
#*****************************************************************************
#Publication message
#*****************************************************************************
echo "********************"
echo "Reproducing files for: https://doi.org/xx.xxxx/xxxxxxxxxxxx"
echo "********************"


#*****************************************************************************
#Select which unit tests to perform based on inputs to this shell script
#*****************************************************************************
#Perform all unit tests if no options are given
tot=11
if [ "$#" = "0" ]; then
     fst=1
     lst=$tot
     echo "Performing all unit tests: $1-$2"
     echo "********************"
fi

#Perform one single unit test if one option is given
if [ "$#" = "1" ]; then
     fst=$1
     lst=$1
     echo "Performing one unit test: $1"
     echo "********************"
fi

#Perform all unit tests between first and second option given (both included)
if [ "$#" = "2" ]; then
     fst=$1
     lst=$2
     echo "Performing unit tests: $1-$2"
     echo "********************"
fi

#Exit if more than two options are given
if [ "$#" -gt "2" ]; then
     echo "A maximum of two options can be used" 1>&2
     exit 22
fi


#*****************************************************************************
#Initialize count for unit tests
#*****************************************************************************
unt=0


#*****************************************************************************
#Define region name
#*****************************************************************************
pfaf=11


#*****************************************************************************
#Fit Errors-in-Variable Regressions to SWOT Observations
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/V_EIV"
mkdir -p "../output_test/EIV_fits"

echo "- Fitting EIV Regressions"

../src/swot_volume_FLaPE-Byrd.py                                               \
    ../input_testing/SWOT/swot_pfaf_${pfaf}_2023-10-01_2024-09-30_testing.csv  \
    ../output_test/V_EIV/swot_vol_pfaf_${pfaf}_2023-10-01_2024-09-30.csv       \
    ../output_test/EIV_fits/swot_vol_fits_${pfaf}_2023-10-01_2024-09-30.csv    \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing computed SWOT volumes (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/V_EIV/swot_vol_pfaf_${pfaf}_2023-10-01_2024-09-30.csv    \
    ../output_test/V_EIV/swot_vol_pfaf_${pfaf}_2023-10-01_2024-09-30.csv       \
    > $cmp_file 2>&1
x=$?
cat $cmp_file
if [ $x -gt 0 ] ; then
    echo "Failed comparison: $cmp_file" >&2
    exit $x
fi
#x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

#echo "- Comparing SWOT volume fit errors (.csv)"
#../src/tst_cmp.py                                                              \
#    ../output_testing/EIV_fits/swot_vol_fits_${pfaf}_2023-10-01_2024-09-30.csv \
#    ../output_test/EIV_fits/swot_vol_fits_${pfaf}_2023-10-01_2024-09-30.csv    \
#    > $cmp_file 2>&1
#    
#cat $cmp_file
#x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Calculate SWOT Volume Anomalies
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/V_anom"

echo "- Calculating SWOT Volume Anomalies"
../src/swot_volume_anomaly.py                                                  \
    ../output_testing/V_EIV/swot_vol_pfaf_${pfaf}_2023-10-01_2024-09-30.csv    \
    ../input_testing/SWOT/swot_pfaf_${pfaf}_2023-10-01_2024-09-30_testing.csv\
    ../output_test/V_anom/V_anom_pfaf_${pfaf}_2023-10-01_2024-09-30.csv        \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing SWOT volume anomalies (.csv)"
../src/tst_cmp.py                                                              \
        ../output_testing/V_anom/V_anom_pfaf_${pfaf}_2023-10-01_2024-09-30.csv \
        ../output_test/V_anom/V_anom_pfaf_${pfaf}_2023-10-01_2024-09-30.csv    \
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Compare MeanDRS volumes to SWOT volumes using MERIT-SWORD translations
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/MeanDRS_comp/SWOT"
mkdir -p "../output_test/MeanDRS_comp/MeanDRS"

echo "- Comparing SWOT and MeanDRS volumes"
../src/meandrs_volume_comp.py                                                  \
    ../output_testing/V_anom/V_anom_pfaf_${pfaf}_2023-10-01_2024-09-30.csv     \
    ../input_testing/MERIT-SWORD/ms_translate/sword_to_mb/sword_to_mb_pfaf_${pfaf}_translate.nc\
    ../input_testing/MERIT-Basins/                                             \
    ../input_testing/MeanDRS/cor/V/                                            \
    ../input_testing/SWORD/SWORD_reaches_v16/                                  \
    ../output_test/MeanDRS_comp/SWOT/V_SWOT_comp_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    ../output_test/MeanDRS_comp/MeanDRS/V_MeanDRS_comp_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing SWOT volume for MeanDRS comparison (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/MeanDRS_comp/SWOT/V_SWOT_comp_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    ../output_test/MeanDRS_comp/SWOT/V_SWOT_comp_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

echo "- Comparing MeanDRS volume for SWOT comparison (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/MeanDRS_comp/MeanDRS/V_MeanDRS_comp_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    ../output_test/MeanDRS_comp/MeanDRS/V_MeanDRS_comp_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Aggregate SWOT-MeanDRS volume comparisons regionally and globally
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/global_summary/MeanDRS_comp/regional"
mkdir -p "../output_test/global_summary/MeanDRS_comp/global"

echo "- Aggregating MeanDRS volume comparison across regions"
../src/meandrs_volume_comp_summary.py                                          \
    ../output_testing/MeanDRS_comp/SWOT/                                       \
    ../output_testing/MeanDRS_comp/MeanDRS/                                    \
    ../output_test/global_summary/MeanDRS_comp/regional/                       \
    ../output_test/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing MeanDRS-SWOT comparison (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    ../output_test/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Calculate MeanDRS volume anomalies at reach subsets for SWOT volume scaling
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/MeanDRS_scale"

echo "- Calculating MeanDRS volume anomalies at reach subsets"
../src/meandrs_volume_scale.py                                                 \
    ../input_testing/MERIT-SWORD/ms_translate/sword_to_mb/sword_to_mb_pfaf_${pfaf}_translate.nc\
    ../input_testing/MERIT-Basins/                                             \
    ../input_testing/MeanDRS/cor/V/                                            \
    ../input_testing/SWORD/SWORD_reaches_v16/                                  \
    ../output_test/MeanDRS_scale/V_SWOT_scale_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing scaled SWOT anomaly (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/MeanDRS_scale/V_SWOT_scale_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    ../output_test/MeanDRS_scale/V_SWOT_scale_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Aggregate scaled SWOT volumes regionally and globally
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/global_summary/MeanDRS_scale/regional"
mkdir -p "../output_test/global_summary/MeanDRS_scale/global"

echo "- Aggregating MeanDRS volume comparison across regions"
../src/meandrs_volume_scale_summary.py                                         \
    ../output_testing/MeanDRS_comp/SWOT/                                       \
    ../output_testing/MeanDRS_comp/MeanDRS/                                    \
    ../output_testing/MeanDRS_scale/                                           \
    ../output_test/global_summary/MeanDRS_scale/regional/                      \
    ../output_test/global_summary/MeanDRS_scale/global/MeanDRS_scale_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing aggregated scaled SWOT anomaly (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/global_summary/MeanDRS_scale/global/MeanDRS_scale_global_summary.csv\
    ../output_test/global_summary/MeanDRS_scale/global/MeanDRS_scale_global_summary.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Compare SWOT-MeanDRS volumes to SWOT volumes using MERIT-SWORD translations
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/MeanDRS_slice/"

echo "- Comparing SWOT and MeanDRS volumes by yearly slice"
../src/meandrs_volume_slice.py                                                 \
    ../output_testing/V_anom/V_anom_pfaf_${pfaf}_2023-10-01_2024-09-30.csv     \
    ../input_testing/MERIT-SWORD/ms_translate/sword_to_mb/sword_to_mb_pfaf_${pfaf}_translate.nc\
    ../input_testing/MERIT-Basins/                                             \
    ../input_testing/MeanDRS/cor/V/                                            \
    ../input_testing/SWORD/SWORD_reaches_v16/                                  \
    ../output_test/MeanDRS_slice/V_SWOT_slice_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing SWOT-MeanDRS yearly slices (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/MeanDRS_slice/V_SWOT_slice_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    ../output_test/MeanDRS_slice/V_SWOT_slice_pfaf_${pfaf}_2023-10-01_2024-09-30.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Aggregate SWOT-MeanDRS volume slices globally
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/global_summary/MeanDRS_slice"

echo "- Aggregating MeanDRS volume slices across regions"
../src/meandrs_volume_slice_summary.py                                         \
    ../output_testing/MeanDRS_slice/                                           \
    ../output_test/global_summary/MeanDRS_slice/MeanDRS_slice_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing aggregated SWOT-MeanDRS yearly slices (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/global_summary/MeanDRS_slice/MeanDRS_slice_global_summary.csv\
    ../output_test/global_summary/MeanDRS_slice/MeanDRS_slice_global_summary.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Assess agreement between SWOT and MeanDRS volume anomalies
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/global_summary/MeanDRS_agree"

echo "- Assessing SWOT-MeanDRS agreement"
../src/meandrs_volume_agreement.py                                             \
    ../output_testing/global_summary/MeanDRS_comp/regional/                    \
    ../output_testing/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    ../output_test/global_summary/MeanDRS_agree/MeanDRS_agree_global_mag_ratio.csv\
    ../output_test/global_summary/MeanDRS_agree/MeanDRS_agree_global_corr.csv  \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing agreement magnitude ratio (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/global_summary/MeanDRS_agree/MeanDRS_agree_global_mag_ratio.csv\
    ../output_test/global_summary/MeanDRS_agree/MeanDRS_agree_global_mag_ratio.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

echo "- Comparing agreement correlation (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/global_summary/MeanDRS_agree/MeanDRS_agree_global_corr.csv\
    ../output_test/global_summary/MeanDRS_agree/MeanDRS_agree_global_corr.csv\
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Pair SWOT volume anomalies to SWORD shapefiles
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/SWORD_reach_anom"

echo "- Pairing SWOT anomalies to SWORD shapefiles"
../src/swot_volume_reach_shp.py                                                \
    ../output_testing/V_anom/                                                  \
    ../input_testing/SWORD/SWORD_reaches_v16/                                  \
    ../output_test/SWORD_reach_anom/                                           \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing SWORD anomaly shapefiles (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/SWORD_reach_anom/SWORD_obs_anom_pfaf_${pfaf}.shp         \
    ../output_test/SWORD_reach_anom/SWORD_obs_anom_pfaf_${pfaf}.shp            \
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Assess proportion of reaches with valid SWOT volume computations
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt
cmp_file=tmp_cmp_$unt.txt

mkdir -p "../output_test/n_obs"

echo "- Assess proportion of reaches with SWOT volumes"
../src/swot_num_obs.py                                                         \
    ../output_testing/V_anom/                                                  \
    ../input_testing/MERIT-SWORD/ms_translate/sword_to_mb/                     \
    ../input_testing/SWORD/SWORD_reaches_v16/                                  \
    ../output_test/n_obs/swot_n_obs.csv                                        \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

echo "- Comparing SWORD anomaly shapefiles (.csv)"
../src/tst_cmp.py                                                              \
    ../output_testing/n_obs/swot_n_obs.csv                                     \
    ../output_test/n_obs/swot_n_obs.csv                                        \
    > $cmp_file 2>&1
x=$? && if [ $x -gt 0 ] ; then echo "Failed comparison: $cmp_file" >&2 ; exit $x ; fi

rm -f $cmp_file
rm -f $run_file
echo "Success"
echo "********************"
fi
