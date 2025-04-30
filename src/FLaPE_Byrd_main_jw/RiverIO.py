#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 13:09:29 2021

@author: mtd
"""

from numpy import array,diff,ones,reshape,empty,nan,isnan,where,logical_not,shape,transpose,logical_and,delete,logical_or,sum,nonzero,arange,linspace
from netCDF4 import Dataset
import pandas as pd
import datetime

class RiverIO:
    # def __init__(self,IOtype,obsFname):
    def __init__(self,IOtype,**fnames):        
        self.type=IOtype        
        self.ObsData={}    
        self.TruthData={}
        
        if self.type == 'MetroManTxt':
            if 'obsFname' in fnames.keys():
                self.obsFname=fnames["obsFname"]
                self.ReadMetroManObs()
            if 'truthFname' in fnames.keys():
                self.truthFname=fnames["truthFname"]
                self.ReadMetroManTruth()                
        elif self.type == 'Confluence':
            if 'obsFname' in fnames.keys():
                self.obsFname=fnames["obsFname"]
                self.ReadConfluenceObs()
        elif self.type == 'USGS-field':
            if 'dataFname' in fnames.keys():
                self.datFname=fnames["dataFname"]
                self.ReadUSGSFieldData()
        elif self.type == 'df':
            if 'obsFname' in fnames.keys():
                self.obsFname=fnames["obsFname"]
                self.ParsePandasDF()
        else:
            print("RiverIO: Undefined observation data format specified. Data not read.")
        
    
    def ReadMetroManObs(self):
        # Read observation file in MetroMan text format        
        fid=open(self.obsFname,"r")
        infile=fid.readlines()
        fid.close()   
        
        # read domain
        self.ObsData["nR"]=eval(infile[1])
                
        buf=infile[3]; buf=buf.split(); self.ObsData["xkm"]=array(buf,float)
        buf=infile[5]; buf=buf.split(); self.ObsData["L"]=array(buf,float)
        self.ObsData["nt"]=eval(infile[7]);
        buf=infile[9]; buf=buf.split(); self.ObsData["t"]=array([buf],float)
        
        #note: move this line to ReachObservations...
        self.ObsData["dt"]=reshape(diff(self.ObsData["t"]).T*86400 * ones((1,self.ObsData["nR"])),(self.ObsData["nR"]*(self.ObsData["nt"]-1),1))
        
        # #specify variable sizes
        self.ObsData["h"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #water surface elevation (wse), [m]
        self.ObsData["h0"]=empty( (self.ObsData["nR"],1)  ) #initial wse, [m]
        self.ObsData["S"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #water surface slope, [-]
        self.ObsData["w"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #river top width, [m]     
        self.ObsData["sigh"]=[] #wse uncertainty standard deviation [m]
        self.ObsData["sigS"]=[] #slope uncertainty standard deviation [-]
        self.ObsData["sigW"]=[] #width uncertainty standard deviation [m]
        
        #% read observations   
        for i in range(0,self.ObsData["nR"]):
            buf=infile[i+11]; buf=buf.split(); self.ObsData["h"][i,:]=array(buf,float)
        
        buf=infile[12+self.ObsData["nR"]]; buf=buf.split(); self.ObsData["h0"]=array(buf,float)
        
        for i in range(0,self.ObsData["nR"]):
            buf=infile[14+self.ObsData["nR"]+i]; buf=buf.split(); self.ObsData["S"][i,:]=array(buf,float)/1e5; #convert cm/km -> m/m
        for i in range(0,self.ObsData["nR"]):
            buf=infile[15+self.ObsData["nR"]*2+i]; buf=buf.split(); self.ObsData["w"][i,:]=array(buf,float)
        self.ObsData["sigS"]=eval(infile[16+self.ObsData["nR"]*3])/1e5; #convert cm/km -> m/m
        self.ObsData["sigh"]=eval(infile[18+self.ObsData["nR"]*3])/1e2; #convert cm -> m
        self.ObsData["sigw"]=eval(infile[20+self.ObsData["nR"]*3] )

        # try removing data with nans
        iUse= logical_not(isnan(self.ObsData['h'][0,:]))
        self.SubSelectData(iUse)

    def ReadMetroManTruth(self):
        
        if not self.ObsData:
            print("RiverIO/ReadMetroManTruth: Canot read truth file if obs data not read in. Truth data not read.")
            return
        
        fid=open(self.truthFname,"r")
        infile=fid.readlines()
        fid.close()  
        
           
        buf=infile[1]; buf=buf.split(); self.TruthData["A0"]=array(buf,float)
        buf=infile[3]; self.TruthData["q"]=buf #not fully implemented; only affects MetroMan plotting routines
        buf=infile[5]; self.TruthData["n"]=buf #not fully implemented; only affects MetroMan plotting routines

        self.TruthData["Q"]=empty( (self.ObsData["nR"],self.ObsData["nt"])  ) #discharge [m^3/s]
        self.TruthData["dA"]=empty( (self.ObsData["nR"],self.ObsData["nt"])  ) #discharge [m^3/s]
        self.TruthData["h"]=empty( (self.ObsData["nR"],self.ObsData["nt"])  ) #discharge [m^3/s]
        self.TruthData["w"]=empty( (self.ObsData["nR"],self.ObsData["nt"])  ) #discharge [m^3/s]
        
        for i in range(0,self.ObsData["nR"]):
            buf=infile[i+7]; buf=buf.split(); self.TruthData["Q"][i,:]=array(buf,float) 
            buf_dA=infile[i+8+self.ObsData["nR"]]; buf_dA=buf_dA.split(); self.TruthData["dA"][i,:]=array(buf_dA,float)
            buf_h=infile[i+9+2*self.ObsData["nR"]]; buf_h=buf_h.split(); self.TruthData["h"][i,:]=array(buf_h,float)
            buf_W=infile[i+10+3*self.ObsData["nR"]]; buf_W=buf_W.split(); self.TruthData["w"][i,:]=array(buf_W,float)
     
    def SubSelectData(self,iUse):
       self.ObsData["nt"]=sum(iUse)           
       self.ObsData["h"]= self.ObsData["h"][:,iUse]
       self.ObsData["w"]= self.ObsData["w"][:,iUse]
       self.ObsData["S"]= self.ObsData["S"][:,iUse]
       #self.ObsData["t"]= self.ObsData["t"][iUse]
       #self.TruthData["Q"]= self.TruthData["Q"][:,iUse]
        
    def ReadConfluenceObs(self):

       #this file is set up to read one reach at a time! variables to be parsed in from SWORD are assigned nan for now

       swot_dataset = Dataset(self.obsFname)

       self.ObsData["nR"]=1
       self.ObsData["xkm"]=nan
       self.ObsData["L"]=nan
       self.ObsData["nt"]=swot_dataset.dimensions["nt"].size

       ts = swot_dataset["reach"]["time"][:].filled(0)
       epoch = datetime.datetime(2000,1,1,0,0,0)
       tall = [ epoch + datetime.timedelta(seconds=t) for t in ts ]
       
       self.ObsData["t"]=array(tall)
       self.ObsData["dt"]=reshape(diff(self.ObsData["t"]).T*86400 * ones((1,self.ObsData["nR"])),(self.ObsData["nR"]*(self.ObsData["nt"]-1),1))

       self.ObsData["h"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #water surface elevation (wse), [m]
       self.ObsData["h0"]=empty( (self.ObsData["nR"],1)  ) #initial wse, [m]
       self.ObsData["S"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #water surface slope, [-]
       self.ObsData["w"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #river top width, [m]     

#       self.ObsData["sigh"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #wse uncertainty, [m]
#       self.ObsData["sigw"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #width uncertainty, [m]
#       self.ObsData["sigS"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) ) #width uncertainty, [m]

       for i in range(0,self.ObsData["nR"]):
            self.ObsData["h"][i,:]=swot_dataset["reach/wse"][0:self.ObsData["nt"]].filled(nan)
            self.ObsData["w"][i,:]=swot_dataset["reach/width"][0:self.ObsData["nt"]].filled(nan)
            self.ObsData["S"][i,:]=swot_dataset["reach/slope2"][0:self.ObsData["nt"]].filled(nan)
#            self.ObsData["sigh"][i,:]=swot_dataset["reach/wse_u"][0:self.ObsData["nt"]].filled(nan)
#            self.ObsData["sigw"][i,:]=swot_dataset["reach/width_u"][0:self.ObsData["nt"]].filled(nan)
#            self.ObsData["sigS"][i,:]=swot_dataset["reach/slope2_u"][0:self.ObsData["nt"]].filled(nan)

       self.ObsData["sigh"]=0.1
       self.ObsData["sigw"]=10.0
       self.ObsData["sigS"]=1.7e-5

       #try cutting out data that are fill value 
       iUse= logical_not(isnan(self.ObsData['h'][0,:]))
       self.SubSelectData(iUse)

       #close dataset
       swot_dataset.close()

    def ReadUSGSFieldData(self):
       df = pd.read_csv(self.datFname,sep='\t',header=[14,15])
       #self.TruthData["Q"]=df.discharge_va.to_numpy() * 0.3048**3 #convert cfs -> cms
       self.TruthData["Q"]=df.chan_discharge.to_numpy() * 0.3048**3 #convert cfs -> cms
       self.TruthData["Q"]=transpose(self.TruthData["Q"])
       self.TruthData["A0"]=nan
       self.ObsData["nR"]=1
       self.ObsData["xkm"]=nan
       self.ObsData["L"]=nan
       self.ObsData["h0"]=nan
       self.ObsData["sigh"]=nan
       self.ObsData["sigw"]=nan
       self.ObsData["sigS"]=nan
       self.ObsData["dt"]=nan
       self.ObsData["nt"]=df.shape[0]
       self.ObsData["S"]=empty([1,self.ObsData["nt"] ])
       self.ObsData["h"]=df.gage_height_va.to_numpy() * 0.3048 #convert ft -> m
       self.ObsData["h"]=transpose(self.ObsData["h"])
       self.ObsData["w"]=df.chan_width.to_numpy() * 0.3048 #convert ft -> m
       self.ObsData["w"]=transpose(self.ObsData["w"])

       self.ObsData["A"]=df.chan_area.to_numpy() * 0.3048**2 #convert ft -> m
       self.ObsData["A"]=transpose(self.ObsData["A"])
       
       iDel=logical_or(isnan(self.ObsData["h"]),isnan(self.TruthData["Q"]))
       iDel=logical_or(iDel,isnan(self.ObsData["A"]))
       iDel=logical_or(iDel,isnan(self.ObsData["w"]))
       iDel=logical_or(iDel,self.ObsData["w"]==0)
       indxDel=where(iDel)
  
       nDel=sum(iDel,axis=1)
  
       self.ObsData["nt"]-=nDel[0]
       self.ObsData["t"]=arange(self.ObsData["nt"])

       self.ObsData["h"]=delete(self.ObsData["h"],indxDel[1],axis=1)
       self.ObsData["w"]=delete(self.ObsData["w"],indxDel[1],axis=1)
       self.ObsData["S"]=delete(self.ObsData["S"],indxDel[1],axis=1)
       self.TruthData["Q"]=delete(self.TruthData["Q"],indxDel[1],axis=1)

       self.ObsData["A"]=delete(self.ObsData["A"],indxDel[1],axis=1)

       self.ObsData["D"]=self.ObsData["A"]/self.ObsData["w"]
    def ParsePandasDF(self):
        hwdata=pd.read_csv(self.obsFname)
        self.ObsData["nt"]=len(hwdata)
        self.ObsData["nR"]=1
        self.ObsData["xkm"]=nan
        self.ObsData["L"]=nan
        self.ObsData["t"]=linspace(1,self.ObsData["nt"],self.ObsData["nt"])
        self.ObsData["dt"]=nan
        self.ObsData["S"]=empty( (1,self.ObsData["nt"]) )
        self.ObsData["h0"]=nan
        
        self.ObsData["sigh"]=.05 # height uncertainty in meters
        self.ObsData["sigS"]=nan
    
        
        #find columns that correspond to height and width
        cols=list(hwdata.columns)
        
        heightcol=''
        widthcol=''        
        for col in cols:            
            if col[0:6]=='Height':
                heightcol=col
            elif col[0:5]=='Width':
                widthcol=col
                
        if widthcol and heightcol:
            print('Parsing data frame, assigning width column=',widthcol,'and height column=',heightcol)
        else:
            print('Unable to parse dataframe')
        
        # assign data
        # self.ObsData["h"]=hwdata[heightcol].values
        # self.ObsData["w"]=hwdata[widthcol].values
        
        #
        self.ObsData["h"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) )
        self.ObsData["w"]=empty(  (self.ObsData["nR"],self.ObsData["nt"]) )
        self.ObsData["h"][0,:]=reshape(hwdata[heightcol].values,(1,self.ObsData["nt"])) 
        self.ObsData["w"][0,:]=reshape(hwdata[widthcol].values,(1,self.ObsData["nt"])) 
        

