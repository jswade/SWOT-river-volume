#!/bin/bash
#*****************************************************************************
#tst_case_dwnl_Wade_etal_2025.sh
#*****************************************************************************
#Purpose:
#This scripts downloads all testing files corresponding to:

#DOI: xx.xxxx/xxxxxxxxxxxx
#The files used are available from:
#DOI: XXX

#Zenodo
#DOI:
#The script returns the following exit codes
# - 0  if all downloads are successful
# - 22 if there was a conversion problem
# - 44 if one download is not successful
#Author:
#Jeffrey Wade, Renato Frasson, Cedric H. David, 2025.

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
echo "Downloading files from:   https://doi.org/XXXXX"
echo "which correspond to   :   https://doi.org/xx.xxxx/xxxxxxxxxxxx"
echo "These files are under a CC BY-NC-SA 4.0 license."
echo "Please cite these two DOIs if using these files for your publications."
echo "********************"


#*****************************************************************************
#Download SWOT-River-Width Zenodo Repository
#*****************************************************************************
echo "- Downloading SWOT-River-Width repository"
#-----------------------------------------------------------------------------
#Download parameters
#-----------------------------------------------------------------------------
URL="https://zenodo.org/records/15428292/files"
folder="../"
list=("input_testing.zip"                                                      \
      "output_testing.zip")

#-----------------------------------------------------------------------------
#Download process
#-----------------------------------------------------------------------------
for ((i = 0; i < ${#list[@]}; i++)); do
    wget -nv -nc $URL/${list[i]} -P $folder
    if [ $? -gt 0 ] ; then echo "Problem downloading ${list[i]}" >&2 ; exit 44 ; fi
    
#-----------------------------------------------------------------------------
#Extract files
#-----------------------------------------------------------------------------
    unzip -nq "${folder}${list[i]}" -d "$folder"
    if [ $? -gt 0 ] ; then echo "Problem extracting ${list[i]}" >&2 ; exit 22 ; fi
    
#-----------------------------------------------------------------------------
#Delete zip files
#-----------------------------------------------------------------------------
    rm "${folder}${list[i]}"
    if [ $? -gt 0 ] ; then echo "Problem deleting ${list[i]}" >&2 ; exit 22 ; fi
done

echo "Success"
echo "********************"

#*****************************************************************************
#Done
#*****************************************************************************


#*****************************************************************************
#Download SWORD files
#*****************************************************************************
echo "- Downloading SWORD files"
#-----------------------------------------------------------------------------
#Download parameters
#-----------------------------------------------------------------------------
URL="https://zenodo.org/records/10013982/files"
folder="../input_testing/SWORD"
dest_folder="${folder}/SWORD_reaches_v16"
list=("SWORD_v16_shp.zip")

#-----------------------------------------------------------------------------
#Download process
#-----------------------------------------------------------------------------
mkdir -p $folder
for file in "${list[@]}"
do
    wget -nv -nc $URL/$file -P $folder/
    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
done

#-----------------------------------------------------------------------------
#Extract files
#-----------------------------------------------------------------------------
unzip -nq "${folder}/${list}" -d "${folder}/${list%.zip}"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Delete files from untested regions (all except pfaf 11)
#-----------------------------------------------------------------------------
find "${folder}" -type f ! -name '*11*' -exec rm {} +
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Relocate reach files from subdirectories
#-----------------------------------------------------------------------------
mkdir -p "$dest_folder"
find "${folder}/${list%.zip}" -type f -name "*reaches*" -exec mv {} "$dest_folder" \;
if [ $? -gt 0 ] ; then echo "Problem moving reach files" >&2 ; exit 22 ; fi

rm -rf "${folder}/${list%.zip}"
if [ $? -gt 0 ] ; then echo "Problem cleaning up" >&2 ; exit 22 ; fi

echo "Success"
echo "********************"

#*****************************************************************************
#Done
#*****************************************************************************


#*****************************************************************************
#Download MERIT-Basins files
#*****************************************************************************
echo "- Downloading MERIT-Basins files"
#-----------------------------------------------------------------------------
#Download parameters from Google Drive
#-----------------------------------------------------------------------------
# Embedded Folder View shows all 61 files, rather than the 50 limited by G.D.
URL="https://drive.google.com/embeddedfolderview?id=1nXMgbDjLLtB9XPwfVCLcF_0"\
"vlYS2M3wy"
folder="../input_testing/MERIT-Basins"

mkdir -p $folder

#Retrieve HTML from Google Drive file view
wget -q -O "${folder}/temphtml" "$URL"
if [ $? -gt 0 ] ; then echo "Problem downloading MERIT-Basins" >&2 ; exit 44 ; fi

#Scrape download id and name for each file from HTML
idlist=($(grep -o '<div class="flip-entry" id="entry-[0-9a-zA-Z_-]*"'         \
    "${folder}/temphtml" | sed 's/^.*id="entry-\([0-9a-zA-Z_-]*\)".*$/\1/'))
if [ $? -gt 0 ] ; then echo "Problem downloading MERIT-Basins" >&2 ; exit 44 ; fi

filelist=($(grep -o '"flip-entry-title">[^<]*<' "${folder}/temphtml" |        \
    sed 's/"flip-entry-title">//; s/<$//'))
if [ $? -gt 0 ] ; then echo "Problem downloading MERIT-Basins" >&2 ; exit 44 ; fi

#Check if lists have same length
if [ ${#filelist[@]} -ne ${#idlist[@]} ]; then echo "Problem downloading MERIT-Basins" \
    >&2 ; exit 44 ; fi

rm "${folder}/temphtml"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Download process, bypassing Google Drive download warning using cookies
#-----------------------------------------------------------------------------
#Download files for pfaf 11
file="${filelist[0]}"
id="${idlist[0]}"

#Save uuid value from server for authentication
wget "https://docs.google.com/uc?export=download&id=1z-l1ICC7X4iKy0vd7FkT5X4u8Ie2l3sy" -O- | sed -rn 's/.*name="uuid" value=\"([0-9A-Za-z_\-]+).*/\1/p' > "${folder}/google_uuid.txt"
if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi

#Download file from server using uuid value
wget -O "${folder}/$file" "https://drive.usercontent.google.com/download?export=download&id=${id}&confirm=t&uuid=$(<"${folder}/google_uuid.txt")"

rm "${folder}/google_uuid.txt"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Unzip files
#-----------------------------------------------------------------------------
unzip -nq "${folder}/$file" -d "${folder}/${file%.zip}"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Move *riv* files and clean up folders
#-----------------------------------------------------------------------------
unzipped_folder="${folder}/${file%.zip}"

# Move only *riv* files
mv "${unzipped_folder}"/*riv* "$folder"
if [ $? -gt 0 ] ; then echo "Problem moving riv files" >&2 ; exit 22 ; fi

# Remove unzipped folder and zip file
rm -r "$unzipped_folder"
rm "${folder}/$file"
if [ $? -gt 0 ] ; then echo "Problem cleaning up files" >&2 ; exit 22 ; fi

echo "Success"
echo "********************"

#*****************************************************************************
#Done
#*****************************************************************************


#*****************************************************************************
#Download MERIT-SWORD files
#*****************************************************************************
echo "- Downloading MERIT-SWORD files"
#-----------------------------------------------------------------------------
#Download parameters
#-----------------------------------------------------------------------------
URL="https://zenodo.org/records/14675925/files"
folder="../input_testing/MERIT-SWORD"
list=("ms_translate.zip")

#-----------------------------------------------------------------------------
#Download process
#-----------------------------------------------------------------------------
mkdir -p $folder
for file in "${list[@]}"
do
    wget -nv -nc $URL/$file -P $folder/
    if [ $? -gt 0 ] ; then echo "Problem downloading $file" >&2 ; exit 44 ; fi
done

#-----------------------------------------------------------------------------
#Extract files
#-----------------------------------------------------------------------------
unzip -nq "${folder}/${list}" -d "$folder"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Delete zip file
#-----------------------------------------------------------------------------
rm "${folder}/${list}"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Delete unneeded files
#-----------------------------------------------------------------------------
rm -rf "${folder}/ms_translate/mb_to_sword"
if [ $? -gt 0 ] ; then echo "Problem deleting mb_to_sword folder" >&2 ; exit 22 ; fi

#-----------------------------------------------------------------------------
#Delete unneeded files that do NOT contain '11'
#-----------------------------------------------------------------------------
find "${folder}/ms_translate/sword_to_mb" -type f ! -name '*11*' -delete
if [ $? -gt 0 ] ; then echo "Problem deleting filtered files in mb_to_sword" >&2 ; exit 22 ; fi

echo "Success"
echo "********************"

#*****************************************************************************
#Done
#*****************************************************************************


#*****************************************************************************
#Download MeanDRS river files
#*****************************************************************************
echo "- Downloading MeanDRS files"
#-----------------------------------------------------------------------------
#Download parameters
#-----------------------------------------------------------------------------
URL="https://zenodo.org/records/10013744/files"
folder="../input_testing/MeanDRS"
list=("V_pfaf_ii_GLDAS_ENS_M_1980-01_2009-12_utc_hig.zip" \
      "V_pfaf_ii_GLDAS_ENS_M_1980-01_2009-12_utc_nrm.zip" \
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
#Move files to MeanDRS folder and delete other folders
#-----------------------------------------------------------------------------
mkdir -p "${folder}/cor/V"
mv "${folder}/${list[0]%.zip}/V_pfaf_11_GLDAS_ENS_M_1980-01_2009-12_utc_hig.nc4"\
   "${folder}/cor/V/V_pfaf_11_GLDAS_COR_M_1980-01_2009-12_utc_hig.nc4"
mv "${folder}/${list[1]%.zip}/V_pfaf_11_GLDAS_ENS_M_1980-01_2009-12_utc_nrm.nc4"\
   "${folder}/cor/V/V_pfaf_11_GLDAS_COR_M_1980-01_2009-12_utc_nrm.nc4"
mv "${folder}/${list[2]%.zip}/V_pfaf_11_GLDAS_ENS_M_1980-01_2009-12_utc_low.nc4"\
   "${folder}/cor/V/V_pfaf_11_GLDAS_COR_M_1980-01_2009-12_utc_low.nc4"

rm -rf "${folder}/${list[0]%.zip}"
rm -rf "${folder}/${list[1]%.zip}"
rm -rf "${folder}/${list[2]%.zip}"
if [ $? -gt 0 ] ; then echo "Problem converting" >&2 ; exit 22 ; fi

echo "Success"
echo "********************"

#*****************************************************************************
#Done
#*****************************************************************************
