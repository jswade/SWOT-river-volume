#!/usr/bin/env python3
"""
Created on Thu Jan 21 04:49:20 2021

# -*- coding: utf-8 -*-
@author: mtd
"""

from scipy import optimize
from numpy import zeros,empty,nan,mean,log,exp,polyfit,array
from ErrorStats import ErrorStats

import matplotlib.pyplot as plt
import warnings

class FlowLawCalibration:
    def __init__(self,D,Qtrue,FlowLaw):
        self.D=D
        self.Qtrue=Qtrue
        self.FlowLaw=FlowLaw
        
        self.param_est=[]
        self.success=[]
        self.Qhat=[]
        self.Performance={}

    def CalibrateReach(self,verbose=True,optmethod='L-BFGS-B',suppress_warnings=False):     
  
        if suppress_warnings:
            warnings.filterwarnings("ignore")
        
        self.success= zeros( 1, dtype=bool )
        self.Qhat=zeros( (1,self.D.nt) )    

        init_params=self.FlowLaw.GetInitParams()
        fl_param_bounds=self.FlowLaw.GetParamBounds()         

        # 1 first try for AHGW only, try using the numpy 'polyfit' function 
        self.success=False
        ls_success=False
        if self.FlowLaw.name ==  'AHGW':
            a,b=self.LeastSquaresFit(self.FlowLaw.W,self.Qtrue)

            if a >= fl_param_bounds[0][0] and a <= fl_param_bounds[0][1] \
               and b >= fl_param_bounds[1][0] and b <= fl_param_bounds[1][1]:
       
               ls_success=True
               self.success=True
               print('... AHGW: polyfit worked!')
 
        # intialize for other calibration
        np=len(init_params)
  
        lb=zeros(np,)
        ub=zeros(np,)
        if np > 1:
            for i in range(np):
                lb[i]=fl_param_bounds[i][0] 
                ub[i]=fl_param_bounds[i][1] 
        else: 
            lb[0]=fl_param_bounds[0]
            ub[0]=fl_param_bounds[1]

        param_bounds=optimize.Bounds(lb,ub)

        # 2 try optimize 'least_squares' function
        if not self.success:
            res = optimize.least_squares(self.ObjectiveFuncRes,
                                init_params,
                                args=([self.Qtrue]),
                                bounds=param_bounds)
 
            if res.success:
                print('... the least_squares solution worked')
                self.success=True
 
        # 3 try the L-BFGS-B function
        if not self.success:
            print('... least_squares failed. Now trying with L-BFGS-B')
            res = optimize.minimize(fun=self.ObjectiveFunc,
                                x0=init_params,
                                args=(self.Qtrue),
                                bounds=param_bounds,
                                method=optmethod,
                                #jac=self.FlowLaw.Jacobian)
                                jac='none')
            if res.success:
                print('... L-BFGS-B succeeded!')
                self.success=True

        if not self.success:
            print('... default algo failed. trying with finite-difference jacobian')
            res = optimize.minimize(fun=self.ObjectiveFunc,
                                x0=init_params,
                                args=(self.Qtrue),
                                bounds=param_bounds,
                                method=optmethod,
                                jac='none')
            if res.success:
                print('... one of the backup algorithm succeeded!')
                self.success=True
 
        if not self.success:
            print('... default algo with f-d jacobian failed. trying another algorithm')
            res = optimize.minimize(fun=self.ObjectiveFunc,
                                x0=init_params,
                                args=(self.Qtrue),
                                bounds=param_bounds,
                                method='trust-constr',
                                jac='none')
                                #jac=self.FlowLaw.Jacobian)
            if res.success:
                print('... one of the backup algorithm succeeded!')
                self.success=True
                            

        if not self.success:
            #retry with bounds required to stay feasible
            param_bounds=optimize.Bounds(lb,ub,keep_feasible=True)
            
            res = optimize.minimize(fun=self.ObjectiveFunc,
                                x0=init_params,
                                args=(self.Qtrue),
                                bounds=param_bounds,
                                method=optmethod,
                                #jac=self.FlowLaw.Jacobian,
                                jac='none',
                                options={'disp':verbose,'maxiter':1e4,'verbose':0})
            if res.success:
                print('... one of the backup algorithm succeeded!')
                self.success=True
        
        if not self.success:
             #retry with a larger step size
             res = optimize.minimize(fun=self.ObjectiveFunc,
                                x0=init_params,
                                args=(self.Qtrue),
                                bounds=param_bounds,
                                method=optmethod,
                                #jac=self.FlowLaw.Jacobian,
                                jac='none',
                                options={'disp':verbose,'maxiter':1e4,'verbose':0,'finite_diff_rel_step':1.0})
             if res.success:
                print('... one of the backup algorithm succeeded!')
                self.success=True

        # ok done trying algorithms... 
        #self.success=res.success

        if not self.success:
            print('FlowLawCalibration: Optimize Failed! Setting flow law parameters to nan')
            self.param_est=empty( len(fl_param_bounds), )
            self.param_est[:]=nan
        else:
            if ls_success:
                self.param_est=array([a,b])
            else:
                self.param_est=res.x

        self.Qhat=self.FlowLaw.CalcQ(self.param_est)      
        
        self.Performance=ErrorStats(self.Qtrue,self.Qhat,self.D)
        self.Performance.CalcErrorStats()

    
    def ObjectiveFunc(self,params,Q):      
        Qhat=self.FlowLaw.CalcQ(params)
        y=sum((Qhat-Q)**2)
        return y

    def ObjectiveFuncRes(self,params,Q):      
        Qhat=self.FlowLaw.CalcQ(params)
        y=Qhat-Q
        return y

    def LeastSquaresFit(self,O,Q):
        # O = observations, either H or W
        # Q = discharge

        y=log(Q)
        x=log(O)
    
        p=polyfit(x,y,1)
    
        a=exp(p[1])
        b=p[0]
    
        return a,b


    def PlotTimeseries(self,PlotTitle='',SaveFilename='',ShowLegend=True):
        fig,ax = plt.subplots()
        ax.plot(self.D.t.T,self.Qtrue,label='gage',marker='o')
        ax.plot(self.D.t.T,self.Qhat,label='estimate',marker='+')        
        plt.title(PlotTitle)
        plt.xlabel('Observation Number')
        plt.ylabel('Discharge $m^3/s$')
        if ShowLegend:
            plt.legend()        
        if SaveFilename:
            plt.savefig(SaveFilename)
        plt.show()
    def PlotScatterplot(self):
        fig,ax = plt.subplots()
        ax.scatter(self.Qtrue,self.Qhat,marker='o')        
        y_lim = ax.get_ylim()
        x_lim = ax.get_xlim()
        onetoone=[0,0]
        onetoone[0]=min(y_lim[0],x_lim[0])
        onetoone[1]=max(y_lim[1],x_lim[1])
        ax.plot([onetoone[0],onetoone[1]],[onetoone[0],onetoone[1]])
        plt.title('Discharge scatterplot')
        plt.xlabel('True Discharge $m^3/s$')
        plt.ylabel('Estimated Discharge $m^3/s$')      
        plt.show()   
    def PlotScatterQW(self,logscale=False):
        fig,ax = plt.subplots()
        ax.scatter(self.FlowLaw.W,self.Qtrue,marker='o')        
        plt.xlabel('Measured width m')
        plt.ylabel('True Discharge $m^3/s$')
        if logscale:
             ax.set_yscale('log')
             ax.set_xscale('log')
        plt.show()   
    def PlotScatterQH(self):
        fig,ax = plt.subplots()
        ax.scatter(self.FlowLaw.H,self.Qtrue,marker='o')        
        plt.xlabel('Measured WSE m')
        plt.ylabel('True Discharge m^3/s')
        plt.show()   
