#!/bin/bash
#*****************************************************************************
#tst_pub_dwnl_Wade_etal_2025.sh
#*****************************************************************************
#Purpose:
#This scripts downloads all files corresponding to:

#DOI: xx.xxxx/xxxxxxxxxxxx
#The files used are available from:

#Zenodo
#DOI: XXXX
#The script returns the following exit codes
# - 0  if all downloads are successful
# - 22 if there was a conversion problem
# - 44 if one download is not successful
#Author:
#Jeffrey Wade, Cedric H. David, 2025.

#*****************************************************************************
#Publication message
#*****************************************************************************
echo "********************"
echo "Reproducing files for: https://doi.org/xx.xxxx/xxxxxxxxx"
echo "********************"


#*****************************************************************************
#Publication message
#*****************************************************************************
echo "********************"
echo "Downloading files from:   https://doi.org/XXXX"
echo "which correspond to   :   https://doi.org/xx.xxxx/xxxxxxxxxxxx"
echo "These files are under a CC BY-NC-SA 4.0 license."
echo "Please cite these two DOIs if using these files for your publications."
echo "********************"


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


##*****************************************************************************
##Download SWORD files
##*****************************************************************************
#echo "- Downloading SWORD files"
##-----------------------------------------------------------------------------
##Download parameters
##-----------------------------------------------------------------------------
#URL="https://zenodo.org/records/10013982/files"
#folder="../input/SWORD"
#dest_folder="${folder}/SWORD_reaches_v16"
#list=("SWORD_v16_shp.zip")
#
#echo "${folder}/${list%.zip}/shp"/*reaches*
#
##-----------------------------------------------------------------------------
##Download process
##-----------------------------------------------------------------------------
#mkdir -p $folder
#for file in "${list[@]}"
#do
#    wget -nv -nc $URL/$file -P $folder/
#    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
#done
#
##-----------------------------------------------------------------------------
##Extract files
##-----------------------------------------------------------------------------
#unzip -nq "${folder}/${list}" -d "${folder}/${list%.zip}"
#if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#
##-----------------------------------------------------------------------------
##Delete zip file
##-----------------------------------------------------------------------------
#rm "${folder}/${list}"
#if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#
##-----------------------------------------------------------------------------
##Relocate reach files from subdirectories
##-----------------------------------------------------------------------------
#mkdir -p "$dest_folder"
#find "${folder}/${list%.zip}" -type f -name "*reaches*" -exec mv {} "$dest_folder" \;
#if [ $? -gt 0 ] ; then echo "Problem moving reach files" >&2 ; exit 22 ; fi
#
#rm -rf "${folder}/${list%.zip}"
#if [ $? -gt 0 ] ; then echo "Problem cleaning up" >&2 ; exit 22 ; fi
#
#echo "Success"
#echo "********************"
#
##*****************************************************************************
##Done
##*****************************************************************************
#
#
##*****************************************************************************
##Download MERIT-Basins files
##*****************************************************************************
#echo "- Downloading MERIT-Basins files"
##-----------------------------------------------------------------------------
##Download parameters from Google Drive
##-----------------------------------------------------------------------------
## Embedded Folder View shows all 61 files, rather than the 50 limited by G.D.
#URL="https://drive.google.com/embeddedfolderview?id=1nXMgbDjLLtB9XPwfVCLcF_0"\
#"vlYS2M3wy"
#folder="../input/MERIT-Basins"
#
#mkdir -p $folder
#
##Retrieve HTML from Google Drive file view
#wget -q -O "${folder}/temphtml" "$URL"
#if [ $? -gt 0 ] ; then echo "Problem downloading MERIT-Basins" >&2 ; exit 44 ; fi
#
##Scrape download id and name for each file from HTML
#idlist=($(grep -o '<div class="flip-entry" id="entry-[0-9a-zA-Z_-]*"'         \
#    "${folder}/temphtml" | sed 's/^.*id="entry-\([0-9a-zA-Z_-]*\)".*$/\1/'))
#if [ $? -gt 0 ] ; then echo "Problem downloading MERIT-Basins" >&2 ; exit 44 ; fi
#
#filelist=($(grep -o '"flip-entry-title">[^<]*<' "${folder}/temphtml" |        \
#    sed 's/"flip-entry-title">//; s/<$//'))
#if [ $? -gt 0 ] ; then echo "Problem downloading MERIT-Basins" >&2 ; exit 44 ; fi
#
##Check if lists have same length
#if [ ${#filelist[@]} -ne ${#idlist[@]} ]; then echo "Problem downloading MERIT-Basins" \
#    >&2 ; exit 44 ; fi
#
#rm "${folder}/temphtml"
#if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#
##-----------------------------------------------------------------------------
##Download process, bypassing Google Drive download warning using cookies
##-----------------------------------------------------------------------------
##Loop through files and ids
#for i in ${!filelist[@]};
#do
#    file="${filelist[i]}"
#    id="${idlist[i]}"
#
#    #Save uuid value from server for authentication
#    wget "https://docs.google.com/uc?export=download&id=1z-l1ICC7X4iKy0vd7FkT5X4u8Ie2l3sy" -O- | sed -rn 's/.*name="uuid" value=\"([0-9A-Za-z_\-]+).*/\1/p' > "${folder}/google_uuid.txt"
#    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
#
#    #Download file from server using uuid value
#    wget -O "${folder}/$file" "https://drive.usercontent.google.com/download?export=download&id=${id}&confirm=t&uuid=$(<"${folder}/google_uuid.txt")"
#
#    rm "${folder}/google_uuid.txt"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#    
#done
#
##-----------------------------------------------------------------------------
##Extract files
##-----------------------------------------------------------------------------
#for file in "${filelist[@]}"
#do
#    unzip -nq "${folder}/$file" -d "${folder}/${filename%.zip}"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#done
#
##-----------------------------------------------------------------------------
##Delete zip files
##-----------------------------------------------------------------------------
#for file in "${filelist[@]}"
#do
#    rm "${folder}/$file"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#done
#
##-----------------------------------------------------------------------------
##Organize files by type
##-----------------------------------------------------------------------------
## Remove cat files
#rm -f "${folder}/cat"*
#if [ $? -gt 0 ] ; then echo "Problem deleting files" >&2 ; exit 22 ; fi
#
#echo "Success"
#echo "********************"
#
##*****************************************************************************
##Done
##*****************************************************************************
#
#
##*****************************************************************************
##Download MERIT-SWORD files
##*****************************************************************************
#echo "- Downloading MERIT-SWORD files"
##-----------------------------------------------------------------------------
##Download parameters
##-----------------------------------------------------------------------------
#URL="https://zenodo.org/records/14675925/files"
#folder="../input/MERIT-SWORD"
#list=("ms_translate.zip")
#
##-----------------------------------------------------------------------------
##Download process
##-----------------------------------------------------------------------------
#mkdir -p $folder
#for file in "${list[@]}"
#do
#    wget -nv -nc $URL/$file -P $folder/
#    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
#done
#
##-----------------------------------------------------------------------------
##Extract files
##-----------------------------------------------------------------------------
#unzip -nq "${folder}/${list}" -d "$folder"
#if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#
##-----------------------------------------------------------------------------
##Delete zip file
##-----------------------------------------------------------------------------
#rm "${folder}/${list}"
#if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#
##-----------------------------------------------------------------------------
##Delete unneeded files
##-----------------------------------------------------------------------------
#rm -rf "${folder}/ms_translate/mb_to_sword"
#if [ $? -gt 0 ] ; then echo "Problem deleting mb_to_sword folder" >&2 ; exit 22 ; fi
#
#echo "Success"
#echo "********************"
#
##*****************************************************************************
##Done
##*****************************************************************************
#

#*****************************************************************************
#Download MeanDRS river files
#*****************************************************************************
echo "- Downloading MeanDRS files"
#-----------------------------------------------------------------------------
#Download parameters
#-----------------------------------------------------------------------------
URL="https://zenodo.org/records/10013744/files"
folder="../input/MeanDRS"
list=("V_pfaf_ii_GLDAS_COR_M_1980-01_2009-12_utc_hig.zip" \
      "V_pfaf_ii_GLDAS_COR_M_1980-01_2009-12_utc_nrm.zip" \
      "V_pfaf_ii_GLDAS_COR_M_1980-01_2009-12_utc_low.zip"\
      "V_pfaf_ii_GLDAS_ENS_M_1980-01_2009-12_utc_hig.zip" \
      "V_pfaf_ii_GLDAS_ENS_M_1980-01_2009-12_utc_nrm.zip"\
      "V_pfaf_ii_GLDAS_ENS_M_1980-01_2009-12_utc_low.zip"
     )

#-----------------------------------------------------------------------------
#Download process
#-----------------------------------------------------------------------------
mkdir -p $folder
for file in "${list[@]}"
do
    wget -nv -nc $URL/$file -P $folder
    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi

#-----------------------------------------------------------------------------
#Extract files
#-----------------------------------------------------------------------------
    unzip -nq "${folder}/${file}" -d "${folder}/${file%.zip}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Delete zip file
#-----------------------------------------------------------------------------
    rm "${folder}/${file}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Find regions missing from COR dataset
#-----------------------------------------------------------------------------
# Get list of ENS regions
regs=$(ls "${folder}/${list[3]%.zip}" | cut -d '_' -f 3 | sort -u)

# Get list of COR regions
regs_cor=$(ls "${folder}/${list[0]%.zip}" | cut -d '_' -f 3 | sort -u)

# Find regions in ENS but not in COR
regs_miss=()
for reg in $regs; do
    if ! echo "$regs_cor" | grep -q "^$reg$"; then
        regs_miss+=($reg)
    fi
done

#-----------------------------------------------------------------------------
#Copy missing region files from ENS to COR: V_pfaf_ii_low
#-----------------------------------------------------------------------------
for reg in ${regs_miss[@]}
do
    cp "${folder}/${list[5]%.zip}/"*${reg}* "${folder}/${list[2]%.zip}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Rename moved files from ENS to COR: V_pfaf_ii_low
#-----------------------------------------------------------------------------
for file in "${folder}/${list[2]%.zip}"/*ENS*
do
    new_fp=$(echo "${file}" | sed 's/ENS/COR/')
    mv "${file}" "${new_fp}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Move files to new folders
#-----------------------------------------------------------------------------
mkdir -p "${folder}/cor/V"
mv "${folder}/${list[2]%.zip}/"*.* "${folder}/cor/V"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Copy missing region files from ENS to COR: V_pfaf_ii_nrm
#-----------------------------------------------------------------------------
for reg in ${regs_miss[@]}
do
    cp "${folder}/${list[4]%.zip}/"*${reg}* "${folder}/${list[1]%.zip}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Rename moved files from ENS to COR: V_pfaf_ii_nrm
#-----------------------------------------------------------------------------
for file in "${folder}/${list[1]%.zip}"/*ENS*
do
    new_fp=$(echo "${file}" | sed 's/ENS/COR/')
    mv "${file}" "${new_fp}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Move files to new folders: V_pfaf_ii_nrm
#-----------------------------------------------------------------------------
mv "${folder}/${list[1]%.zip}/"*.* "${folder}/cor/V"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Copy missing region files from ENS to COR: V_pfaf_ii_hig
#-----------------------------------------------------------------------------
for reg in ${regs_miss[@]}
do
    cp "${folder}/${list[3]%.zip}/"*${reg}* "${folder}/${list[0]%.zip}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Rename moved files from ENS to COR: V_pfaf_ii_hig
#-----------------------------------------------------------------------------
for file in "${folder}/${list[0]%.zip}"/*ENS*
do
    new_fp=$(echo "${file}" | sed 's/ENS/COR/')
    mv "${file}" "${new_fp}"
    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
done

#-----------------------------------------------------------------------------
#Move files to new folders: V_pfaf_ii_hig
#-----------------------------------------------------------------------------
mv "${folder}/${list[0]%.zip}/"*.* "${folder}/cor/V"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
##Delete other folders
#-----------------------------------------------------------------------------
for file in "${list[@]}"; do
  zip_path="${folder}/${file}"
  dir_path="${folder}/${file%.zip}"

  if [ ! -f "$zip_path" ] && [ -d "$dir_path" ]; then
    echo "Deleting $dir_path"
    rm -rf "$dir_path"
  fi
done

echo "Success"
echo "********************"

#*****************************************************************************
#Done
#*****************************************************************************

#
##*****************************************************************************
##Download HYBAS global files
##*****************************************************************************
##-----------------------------------------------------------------------------
##Download parameters
##-----------------------------------------------------------------------------
#URL="https://data.hydrosheds.org/file/HydroBASINS/standard"
#folder="../input/hybas_global"
#list=("hybas_af_lev02_v1c.zip"                                                \
#      "hybas_ar_lev02_v1c.zip"                                                \
#      "hybas_as_lev02_v1c.zip"                                                \
#      "hybas_au_lev02_v1c.zip"                                                \
#      "hybas_eu_lev02_v1c.zip"                                                \
#      "hybas_gr_lev02_v1c.zip"                                                \
#      "hybas_na_lev02_v1c.zip"                                                \
#      "hybas_sa_lev02_v1c.zip"                                                \
#      "hybas_si_lev02_v1c.zip"                                                \
#     )
#
##-----------------------------------------------------------------------------
##Download process
##-----------------------------------------------------------------------------
#mkdir -p $folder
#for file in "${list[@]}"
#do
#    wget -nv -nc $URL/$file -P $folder
#    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
#done
#
##-----------------------------------------------------------------------------
##Extract files
##-----------------------------------------------------------------------------
#for file in "${list[@]}"
#do
#    unzip -nq "${folder}/${file}" -d "${folder}/${file%.zip}"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#done
#
##-----------------------------------------------------------------------------
##Delete zip file
##-----------------------------------------------------------------------------
#for file in "${list[@]}"
#do
#    rm "${folder}/${file}"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#done
#
##-----------------------------------------------------------------------------
##Move shapefiles to hybas_global
##-----------------------------------------------------------------------------
#root_dir="../input/hybas_global"
#
## Define allowed extensions
#exts=("dbf" "shp" "shx" "prj" "sbn" "sbx")
#
## Loop over all subdirectories
#for subdir in "$root_dir"/*/; do
#    # Skip if not a directory
#    [ -d "$subdir" ] || continue
#
#    # Move matching files
#    for ext in "${exts[@]}"; do
#        for f in "$subdir"*."$ext"; do
#            [ -e "$f" ] || continue  # skip if no file exists
#            mv "$f" "$root_dir/"
#            if [ $? -gt 0 ]; then
#                echo "Problem moving $f" >&2
#                exit 22
#            fi
#        done
#    done
#done
#
##-----------------------------------------------------------------------------
## Delete extracted folders
##-----------------------------------------------------------------------------
#for file in "${list[@]}"; do
#    folder_to_delete="${folder}/${file%.zip}"
#    rm -rf "$folder_to_delete"
#    if [ $? -gt 0 ]; then
#        echo "Problem deleting folder $folder_to_delete" >&2
#        exit 22
#    fi
#done
#
##-----------------------------------------------------------------------------
## Merge all shapefiles in /hybas_global/ into one global shapefile
##-----------------------------------------------------------------------------
#input_dir="../input/hybas_global"
#output_shp="${input_dir}/hybas_global_lev02_v1c.shp"
#
## Remove any existing merged file
#rm -f "${output_shp%.shp}."*
#
## Merge files
#first=1
#for shp in "${input_dir}"/*.shp; do
#    if [ $first -eq 1 ]; then
#        ogr2ogr "$output_shp" "$shp"
#        first=0
#    else
#        ogr2ogr -update -append "$output_shp" "$shp" -nln "$(basename "$output_shp" .shp)"
#    fi
#
#    if [ $? -gt 0 ]; then
#        echo "Problem merging shapefile: $shp" >&2
#        exit 22
#    fi
#done
#
##-----------------------------------------------------------------------------
## Merge all shapefiles in /hybas_regional/ into one global shapefile
##-----------------------------------------------------------------------------
## Delete all individual shapefile components (but not the merged one)
#find ../input/hybas_global -type f \( \
#    -name "*.shp" -o -name "*.shx" -o -name "*.dbf" -o -name "*.prj" -o \
#    -name "*.sbn" -o -name "*.sbx" -o -name "*.cpg" -o -name "*.qix" \) \
#    ! -name "hybas_global_lev02_v1c.*" -delete
#
#echo "Success"
#echo "********************"
#
##*****************************************************************************
##Done
##*****************************************************************************
#
#
##*****************************************************************************
##Download Natural Earth files
##*****************************************************************************
##-----------------------------------------------------------------------------
##Download parameters
##-----------------------------------------------------------------------------
#URL=("https://naciscdn.org/naturalearth")
#folder="../input/natural_earth"
#list=("50m/physical/ne_50m_graticules_30.zip"                                 \
#      "110m/physical/ne_110m_land.zip"                                        \
#     )
#files=("ne_50m_graticules_30.zip"\
#       "ne_110m_land.zip"
#       )
#
##-----------------------------------------------------------------------------
##Download process
##-----------------------------------------------------------------------------
#mkdir -p $folder
#for file in "${list[@]}"
#do
#    wget -nv -nc $URL/$file -P $folder
#    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
#done
#
##-----------------------------------------------------------------------------
##Extract files
##-----------------------------------------------------------------------------
#for file in "${files[@]}"
#do
#    unzip -nq "${folder}/${file}" -d "${folder}/${file%.zip}"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#done
#
##-----------------------------------------------------------------------------
##Delete zip file
##-----------------------------------------------------------------------------
#for file in "${files[@]}"
#do
#    rm "${folder}/${file}"
#    if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi
#done
#
##-----------------------------------------------------------------------------
##Create Antartica only ne_110m_land file
##-----------------------------------------------------------------------------
#ogr2ogr \
#  ../input/natural_earth/ne_110m_land/ne_110m_land_antarctica.shp \
#  ../input/natural_earth/ne_110m_land/ne_110m_land.shp \
#  -sql "SELECT * FROM ne_110m_land WHERE FID = 7"
#
#echo "Success"
#echo "********************"
#
##*****************************************************************************
##Done
##*****************************************************************************
#
#
##*****************************************************************************
##Download SWOT Reach Observations for each Region
##*****************************************************************************
#mkdir -p "../input/SWOT/global_obs"
#
#echo "- Selecting SWORD nodes in target area"
#for ((i = 0; i < ${#reg[@]}; i++)); do
#
#    echo $i
#
#    ../src/swot_dwnl_hydrocron.py                                              \
#        ../input/SWORD/SWORD_reaches_v16/${reg[i]}_sword_reaches_hb${pfaf[i]}_v16.shp\
#        "2023-10-01"                                                           \
#        "2024-09-30"                                                           \
#        ../input/SWOT/swot_pfaf_${pfaf[i]}_2023-10-01_2024-09-30.csv           \
#        > $run_file
#    x=$? && if [ $x -gt 0 ] ; then echo "Failed run: $run_file" >&2 ; exit $x ; fi
#
#done
#
#echo "Success"
#echo "********************"
#
##*****************************************************************************
##Done
##*****************************************************************************
