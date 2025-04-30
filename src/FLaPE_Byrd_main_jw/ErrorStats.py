#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 14:12:54 2021

@author: mtd
"""

from numpy import mean,sqrt,log,std,corrcoef,quantile

class ErrorStats:
    
    def __init__(self,Qt,Qhat,D):
    
        self.Qt=Qt
        self.Qhat=Qhat
        self.D=D
    
        self.RMSE=[];

    def CalcErrorStats(self):
        
        QhatAvg=mean(self.Qhat,axis=0)
        
        self.RMSE=sqrt(mean( (self.Qt-self.Qhat)**2 ) )
        
        self.rRMSE=sqrt(mean( ((self.Qt-self.Qhat)/self.Qt)**2  ) )        
        self.nRMSE=self.RMSE/mean(self.Qt)
          
        res=self.Qhat-self.Qt
        logr=log(self.Qhat)-log(self.Qt)

        Rmatrix=corrcoef(self.Qhat,self.Qt)
        
        self.NSE=1.-sum(res**2)/sum(  (self.Qt-QhatAvg)**2  )        
        
        self.VE=1.-sum(abs(res))/sum(self.Qt)
        
        self.bias=mean(res)
                        
        self.stdresid=std(res)        
        
        self.nbias = self.bias/QhatAvg
    
        self.MSC=log(  sum((self.Qt-QhatAvg)**2)/sum(res**2) -2*2 / self.D.nt  )
        self.meanLogRes=mean(logr)
        self.stdLogRes=std(logr)
        self.meanRelRes=mean(res/self.Qt)
        self.stdRelRes=std(res/self.Qt)

        self.r=Rmatrix[0,1]

        beta=mean(self.Qhat)/mean(self.Qt)
        CVhat=std(self.Qhat)/mean(self.Qhat)
        CVt=std(self.Qt)/mean(self.Qt)
        gamma=CVhat/CVt
        self.KGE=1-sqrt( (self.r-1)**2 + (beta-1)**2 + (gamma-1)**2  )

        self.anr67=quantile(abs( res/self.Qt ),0.67)

        self.nMAE=mean(abs(res))/mean(self.Qt)
    
        self.Qbart=mean(self.Qt)  
    
    def ShowKeyErrorMetrics(self):
        print('Normalized RMSE:', '%.2f'%self.nRMSE)
        print('nMAE:', '%.2f'%self.nMAE)        
        print('r:', '%.2f'%self.r)        
        print('KGE:', '%.2f'%self.KGE)        
        print('NSE:', '%.2f'%self.NSE)        
        print('RMSE/std(Q):', '%.2f'%(self.RMSE/std(self.Qt)))        
