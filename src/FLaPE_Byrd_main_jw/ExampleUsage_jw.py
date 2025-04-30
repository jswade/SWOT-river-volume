#!/usr/bin/env python3
# ******************************************************************************
# ExampleUsage_jw.py
# ******************************************************************************

# Purpose:
# Convert ExampleUsage.ipynb of FLaPE-Byrd to  .py
# Author:
# Jeffrey Wade, 2024


# 1) add FLaPE-Byrd repository location (pulled from github.com/mikedurand/flape-byrd) to the path
import sys
sys.path.append('/Users/mtd/GitHub/FLaPE-Byrd/') 

# 2) import needed modules
from ReachObservations import ReachObservations
from ReachTruth import ReachTruth
from RiverIO import RiverIO
from FlowLawCalibration import FlowLawCalibration
from Domain import Domain
from pprint import pprint
from FlowLaws import MWACN,MWAPN,AHGW,AHGD,MWHCN,MWAVN,MOMMA,MWHFN,PVK

# 3) provide path to reach averaged Sagavanirktok data from hi-res commercial imagery, and read data in
BaseDir='ArcticDEMSag/'
#BaseDir='PepsiSac/'
IO=RiverIO('MetroManTxt',obsFname=BaseDir+'SWOTobs.txt',truthFname=BaseDir+'truth.txt')

# 4) Set up data objects
D=Domain(IO.ObsData)
Obs=ReachObservations(D,IO.ObsData,True,3)
Truth=ReachTruth(IO.TruthData)

# The Obs class supports spatially and temporally varying data. 
# This example notebook uses the first reach in the data.
ReachDict={}
ReachDict['dA']=Obs.dA[0,:]
ReachDict['w']=Obs.w[0,:]
ReachDict['S']=Obs.S[0,:]
ReachDict['H']=Obs.h[0,:]            
ReachDict['Qtrue']=Truth.Q[0,:]