#!/bin/bash
#*****************************************************************************
#swot_dwnl.sh
#*****************************************************************************

#Purpose:
#This script reproduces analysis steps to download SWOT reach observations
#from Hydrocron.

#DOI: xx.xxxx/xxxxxxxxxxxx
#The files used are available from:

#Zenodo
#DOI:
#The script returns the following exit codes
# - 0  if all downloads are successful
# - 22 if there was a conversion problem
# - 44 if one download is not successful
#Author:
#Jeffrey Wade, Cedric H. David, 2024.

#*****************************************************************************
#Publication message
#*****************************************************************************
echo "********************"
echo "Reproducing files for: https://doi.org/xx.xxxx/xxxxxxxxx"
echo "********************"


#*****************************************************************************
#Select which unit tests to perform based on inputs to this shell script
#*****************************************************************************
#Perform all unit tests if no options are given
tot=1
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
#Download SWOT Reach Observations for each Region
#*****************************************************************************
unt=$((unt+1))
if (("$unt" >= "$fst")) && (("$unt" <= "$lst")) ; then
echo "Running unit test $unt/$tot"

run_file=tmp_run_$unt.txt

mkdir -p "../input/SWOT/global_obs"

echo "- Selecting SWORD nodes in target area"
for ((i = 0; i < ${#reg[@]}; i++)); do

    echo $i

    ../src/swot_dwnl_hydrocron.py                                              \
        ../input/SWORD/SWORD_reaches_v16/${reg[i]}_sword_reaches_hb${pfaf[i]}_v16.shp\
        "2023-10-01"                                                           \
        "2024-09-30"                                                           \
        ../input/SWOT/global_obs/swot_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv\
        > $run_file
    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi

done

rm -f $run_file
echo "Success"
echo "********************"
fi
