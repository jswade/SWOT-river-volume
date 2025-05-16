#!/bin/bash
#*****************************************************************************
#tst_pub_repr_all_Wade_etal_2025.sh
#*****************************************************************************
#Purpose:
#This script reproduces all pre- and post-processing steps used in the
#writing of:

#DOI: xx.xxxx/xxxxxxxxxxxx

#Zenodo
#DOI: XXXXXX
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
tot=23
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
#Define file and region names
#*****************************************************************************
reg=(
     "af"
     "af"
     "af"
     "af"
     "af"
     "af"
     "af"
     "af"
     "eu"
     "eu"
     "eu"
     "eu"
     "eu"
     "eu"
     "eu"
     "eu"
     "eu"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "as"
     "oc"
     "oc"
     "oc"
     "oc"
     "oc"
     "oc"
     "oc"
     "sa"
     "sa"
     "sa"
     "sa"
     "sa"
     "sa"
     "sa"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     "na"
     )
       
pfaf=(
      11
      12
      13
      14
      15
      16
      17
      18
      21
      22
      23
      24
      25
      26
      27
      28
      29
      31
      32
      33
      34
      35
      36
      41
      42
      43
      44
      45
      46
      47
      48
      49
      51
      52
      53
      54
      55
      56
      57
      61
      62
      63
      64
      65
      66
      67
      71
      72
      73
      74
      75
      76
      77
      78
      81
      82
      83
      84
      85
      86
      91
      )


#*****************************************************************************
#Fit Errors-in-Variable Regressions to SWOT Observations
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt

mkdir -p "../output/V_EIV"
mkdir -p "../output/EIV_fits"

echo "- Fitting EIV Regressions"
for ((i = 0; i < ${#pfaf[@]}; i++)); do

    echo $i

    ../src/swot_volume_FLaPE-Byrd.py                                           \
        ../input/SWOT/swot_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv           \
        ../output/V_EIV/swot_vol_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv     \
        ../output/EIV_fits/swot_vol_fits_${pfaf[i]}_2023-10-01_2024-09-30.csv  \
        > $run_file
    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

done

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

mkdir -p "../output/V_anom"

echo "- Calculating SWOT Volume Anomalies"
for ((i = 0; i < ${#pfaf[@]}; i++)); do

    echo $i

    ../src/swot_volume_anomaly.py                                       \
        ../output/V_EIV/swot_vol_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        ../input/SWOT/swot_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        ../output/V_anom/V_anom_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv \
        > $run_file
    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

done

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

mkdir -p "../output/MeanDRS_comp/SWOT"
mkdir -p "../output/MeanDRS_comp/MeanDRS"

echo "- Comparing SWOT and MeanDRS volumes"
for ((i = 0; i < ${#pfaf[@]}; i++)); do

    echo $i

    ../src/meandrs_volume_comp.py                                       \
        ../output/V_anom/V_anom_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv \
        ../input/MERIT-SWORD/ms_translate/sword_to_mb/sword_to_mb_pfaf_${pfaf[i]}_translate.nc\
        ../input/MERIT-Basins/                                                 \
        ../input/MeanDRS/cor/V/                                                \
        ../input/SWORD/SWORD_reaches_v16/                                      \
        ../output/MeanDRS_comp/SWOT/V_SWOT_comp_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        ../output/MeanDRS_comp/MeanDRS/V_MeanDRS_comp_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        > $run_file
    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

done

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

mkdir -p "../output/global_summary/MeanDRS_comp/regional"
mkdir -p "../output/global_summary/MeanDRS_comp/global"

echo "- Aggregating MeanDRS volume comparison across regions"
../src/meandrs_volume_comp_summary.py                                          \
    ../output/MeanDRS_comp/SWOT/                                          \
    ../output/MeanDRS_comp/MeanDRS/                                       \
    ../output/global_summary/MeanDRS_comp/regional/                       \
    ../output/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

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

mkdir -p "../output/MeanDRS_scale"

echo "- Calculating MeanDRS volume anomalies at reach subsets"
for ((i = 0; i < ${#pfaf[@]}; i++)); do

    echo $i

    ../src/meandrs_volume_scale.py                                      \
        ../input/MERIT-SWORD/ms_translate/sword_to_mb/sword_to_mb_pfaf_${pfaf[i]}_translate.nc\
        ../input/MERIT-Basins/                                                 \
        ../input/MeanDRS/cor/V/                                                \
        ../input/SWORD/SWORD_reaches_v16/                                      \
        ../output/MeanDRS_scale/V_SWOT_scale_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        > $run_file
    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

done

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

mkdir -p "../output/global_summary/MeanDRS_scale/regional"
mkdir -p "../output/global_summary/MeanDRS_scale/global"

echo "- Aggregating MeanDRS volume comparison across regions"
../src/meandrs_volume_scale_summary.py                                         \
    ../output/MeanDRS_comp/SWOT/                                          \
    ../output/MeanDRS_comp/MeanDRS/                                       \
    ../output/MeanDRS_scale/                                              \
    ../output/global_summary/MeanDRS_scale/regional/                      \
    ../output/global_summary/MeanDRS_scale/global/MeanDRS_scale_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

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

mkdir -p "../output/MeanDRS_slice/"

echo "- Comparing SWOT and MeanDRS volumes by yearly slice"
for ((i = 0; i < ${#pfaf[@]}; i++)); do

    echo $i

    ../src/meandrs_volume_slice.py                                      \
        ../output/V_anom/V_anom_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv \
        ../input/MERIT-SWORD/ms_translate/sword_to_mb/sword_to_mb_pfaf_${pfaf[i]}_translate.nc\
        ../input/MERIT-Basins/                                                 \
        ../input/MeanDRS/cor/V/                                                \
        ../input/SWORD/SWORD_reaches_v16/                                      \
        ../output/MeanDRS_slice/V_SWOT_slice_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        > $run_file
    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

done

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

mkdir -p "../output/global_summary/MeanDRS_slice"

echo "- Aggregating MeanDRS volume slices across regions"
../src/meandrs_volume_slice_summary.py                                         \
    ../output/MeanDRS_slice/                                              \
    ../output/global_summary/MeanDRS_slice/MeanDRS_slice_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi
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

mkdir -p "../output/global_summary/MeanDRS_agree"

echo "- Assessing SWOT-MeanDRS agreement"
../src/meandrs_volume_agreement.py                                             \
    ../output/global_summary/MeanDRS_comp/regional/                       \
    ../output/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    ../output/global_summary/MeanDRS_agree/MeanDRS_agree_global_mag_ratio.csv\
    ../output/global_summary/MeanDRS_agree/MeanDRS_agree_global_corr.csv  \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi
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

mkdir -p "../output/SWORD_reach_anom"

echo "- Pairing SWOT anomalies to SWORD shapefiles"
../src/swot_volume_reach_shp.py                                                \
    ../output/V_anom/                                                     \
    ../input/SWORD/SWORD_reaches_v16/                                          \
    ../output/SWORD_reach_anom/                                           \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi
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

mkdir -p "../output/n_obs"

echo "- Assess proportion of reaches with SWOT volumes"
../src/swot_num_obs.py                                                         \
    ../output/V_anom/                                                     \
    ../input/MERIT-SWORD/ms_translate/sword_to_mb/                             \
    ../input/SWORD/SWORD_reaches_v16/                                          \
    ../output/n_obs/swot_n_obs.csv                                        \
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

rm -f $run_file
echo "Success"
echo "********************"
fi


#*****************************************************************************
#Creating SWOT volume comparison plots
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt

echo "- Generating plots"
../src/swot_volume_plots.py                                                    \
    ../output/global_summary/MeanDRS_comp/regional/                       \
    ../output/global_summary/MeanDRS_comp/global/MeanDRS_comp_global_summary.csv\
    ../output/global_summary/MeanDRS_scale/regional/                      \
    ../output/global_summary/MeanDRS_scale/global/MeanDRS_scale_global_summary.csv\
    ../output/MeanDRS_slice/                                              \
    ../output/global_summary/MeanDRS_slice/MeanDRS_slice_global_summary.csv\
    > $run_file
x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

rm -f $run_file
echo "Success"
echo "********************"
fi
