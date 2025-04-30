#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 22:11:07 2021

@author: mtd
"""

from numpy import concatenate, zeros, tril,ones

class Domain:
    def __init__(self,RiverData):
        self.nR=RiverData["nR"] #number of reaches
        self.xkm=RiverData["xkm"] #reach midpoint distance downstream [m]
        self.L=RiverData["L"]  #reach lengths, [m]
        self.nt=RiverData["nt"] #number of overpasses
        self.t=RiverData["t"] #time, [days]
        self.dt=RiverData["dt"] #time delta between successive overpasses, [seconds]
        
        
    def CalcU(self):
            
        M=self.nR * self.nt
        N=self.nR *(self.nt-1)
        
        u=concatenate( (zeros( (1,self.nt-1) ), tril(ones( (self.nt-1,self.nt-1) )) ),0  )
        
        U=zeros( (M,N) )
        
        for i in range(0,self.nR):
            a=self.nt*i
            b=self.nt*i+self.nt
            c=(self.nt-1)*i
            d=(self.nt-1)*i+(self.nt-1)
            U[a:b,c:d  ] = u   
            
        return U