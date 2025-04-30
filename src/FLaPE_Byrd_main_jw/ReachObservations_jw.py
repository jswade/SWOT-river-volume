#/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 23:49:40 2021
@author: mtd
"""

from numpy import reshape,concatenate,zeros,ones,triu,empty,arctan,tan,pi,std,\
   mean,sqrt,var,cov,inf,polyfit,linspace,array,median,piecewise,nanmedian
import numpy as np
from scipy import stats,optimize
import matplotlib.pyplot as plt
import copy
import warnings

class ReachObservations:    
        
    def __init__(self,D,RiverData,ConstrainHWSwitch=False,CalcAreaFitOpt=0,dAOpt=0,Verbose=False,σW=[]):
        
        """  Initialize ReachObservation Ojbect. 
            Input Arguments:
                CalcAreaFitOpt= 
                    0 : don't calculate;  
                    1 : use equal-spaced breakpoints; 
                    2 : optimize breakpoints & fits together
                    3 : optimize breakpoints, then optimize fits
                dAOpt= 
                    0 : use MetroMan style calculation; 
                    1 : use SWOT L2 style calculation

            Flow:
                1. Assign data
                2. Calc height-width fits
                3. Constrain height-width data
                4. Calculate areas
        """

        if ConstrainHWSwitch and CalcAreaFitOpt== 0:
            print('If you want to use Fluvial Hypsometry constraint, you also need to do CalcAreaFitOpt > 0')
            print('Stopping ReachObservations init function...')
            return
        
        self.D=D    
        self.CalcAreaFitOpt=CalcAreaFitOpt
        self.ConstrainHWSwitch=ConstrainHWSwitch
        self.Verbose=Verbose

        # 1 assign data from input dictionary
        self.h=copy.deepcopy(RiverData["h"])        
        self.w=copy.deepcopy(RiverData["w"])
        self.S=RiverData["S"]
        self.h0=RiverData["h0"]
        self.sigh=RiverData["sigh"]
        if not (σW):
            self.sigw=RiverData["sigw"]
        else:
            self.sigw=σW
        self.sigS=RiverData["sigS"]    


        # 2 calculate Area (i.e. H-W) fits for 3 sub-domain using EIV model a la SWOT
        if self.CalcAreaFitOpt > 0:
            #caution! right now this only runs on reach 0 in this set. 
            self.CalcAreaFits()

            # not sure what this was intended to do...
            #if ("area_fit") not in globals() :
            #    dAOpt=-1 
        
        # 3 constrain heights and widths to be self-consistent
        self.ConstrainHW()

        if self.Verbose:
            self.plotHW()

        # create resahepd versions of constrained observations
        self.hv=reshape(self.h, (self.D.nR*self.D.nt,1) )
        self.Sv=reshape(self.S, (self.D.nR*self.D.nt,1) )
        self.wv=reshape(self.w, (self.D.nR*self.D.nt,1) )
        
        # 4 calculate areas
        #   check area calculation option
        if dAOpt==1 and ( "area" not in globals() ):
             if self.Verbose:
                  print('Warning: ReachObservations tried to use', 
                     'SWOT-style area calcs, but no area function available.')
                  print('Using MetroMan-style instead')
             dAOpt=0

        # calculate
        if dAOpt == 0:
             if self.Verbose:
                print('MetroMan-style area calculations')
             DeltaAHat=empty( (self.D.nR,self.D.nt-1) )
             self.DeltaAHatv = self.calcDeltaAHatv(DeltaAHat)
             self.dA= concatenate(  (zeros( (self.D.nR,1) ), DeltaAHat @ triu(ones( (self.D.nt-1,self.D.nt-1) ),0)),1 )
             self.dAv=self.D.CalcU() @ self.DeltaAHatv
        elif dAOpt == 1:
             if self.Verbose:
                print('SWOT-style area calculations')
             self.dA=empty( (self.D.nR,self.D.nt)   )
             for t in range(self.D.nt):
                 self.dA[0,t],what,hhat,dAUnc=area(self.h[0,t],self.w[0,t],self.area_fit)
                 #if ConstrainHWSwitch and not np.isnan(hhat):
                 #    self.h[0,t]=hhat
                 #    self.w[0,t]=what
             
             if self.Verbose:
                     self.plotHdA()

    def calcDeltaAHatv(self, DeltaAHat):
        
        for r in range(0,self.D.nR):
            for t in range(0,self.D.nt-1):
                DeltaAHat[r,t]=(self.w[r,t]+self.w[r,t+1])/2 * (self.h[r,t+1]-self.h[r,t])
         
        # changed how this part works compared with Matlab, avoiding translating calcU
        return reshape(DeltaAHat,(self.D.nR*(self.D.nt-1),1) )
    
    def ConstrainHW(self):
        
        if self.CalcAreaFitOpt == 0:
            # calculate single sub-domain height-width-area fits and project data
            #   onto calculated line
            self.hobs=copy.deepcopy(self.h[0,:])
            self.wobs=copy.deepcopy(self.w[0,:])

            #range-normalize data
            x=self.hobs
            y=self.wobs
            x_range=max(x)-min(x)        
            x_mean=mean(x) 
            xn=(x-x_mean)/x_range
            y_range=max(y)-min(y)        
            y_mean=mean(y) 
            yn=(y-y_mean)/y_range
        
            #[m,b]=self.FitLOC(xn,yn)
            [m,b]=self.FitEIV(xn,yn)
            mo=-tan(pi/2-arctan(m))
 
            #projet w,h onto LOC or EIV
            hhatn=(yn-mo*xn-b)/(m-mo)
            whatn=m*hhatn+b

            #un-normalize data
            hhat=hhatn*x_range+x_mean
            what=whatn*y_range+y_mean

            hres=self.h[0,:]-hhat
            wres=self.w[0,:]-what

            self.stdh_LOChat=std(hres)
            self.stdw_LOChat=std(wres)

            if self.ConstrainHWSwitch:
                 self.h[0,:]=hhat
                 self.w[0,:]=what
        else: # if there are three sub-domains
            self.hobs=copy.deepcopy(self.h[0,:])
            self.wobs=copy.deepcopy(self.w[0,:])

            hhat=np.empty((1,self.D.nt))
            what=np.empty((1,self.D.nt))

            for i in range(self.D.nt):
                hhat[0,i],what[0,i]=self.MapPointToHypsometricCurve(self.hobs[i],self.wobs[i])

            if self.ConstrainHWSwitch:
                 self.h[0,:]=hhat[0,:]
                 self.w[0,:]=what[0,:]
                 
################################################################################     
            # JW: Change to nanmin to allow for nan values for fail to constrain pts
            self.area_fit['h_break'][0]=np.nanmin(hhat)
################################################################################     
################################################################################     
            # JW: Change to nanmin to allow for nan values for fail to constrain pts
            self.area_fit['h_break'][3]=np.nanmax(hhat)
################################################################################     
                

    def MapPointToHypsometricCurve(self,h,w):
        sds=[0,1,2]

        hhat=np.nan
        what=np.nan

        for sd in sds:
            hhatsd,whatsd = self.MapPointToSubDomain(sd,h,w)

            #print('for subdomain',sd,'mapped point=',hhatsd,whatsd)

            DataInSubdomain = (hhatsd >= self.area_fit['h_break'][sd] and hhatsd < self.area_fit['h_break'][sd+1] )
            DataValidExtrapLow = (sd ==0 and hhatsd < self.area_fit['h_break'][0])
            DataValidExtrapHi = (sd == 2 and hhatsd > self.area_fit['h_break'][2])
            DataValidExtrap = DataValidExtrapHi or DataValidExtrapLow

            if DataInSubdomain or DataValidExtrap:
                hhat=hhatsd
                what=whatsd

        if np.isnan(hhat):
            print('data point h = ' + str(h) + ', w = ' + str(w) + ' did not map to a valid sub-domain...')
            
################################################################################     
            # JW EDITS: Map nan point to breakpoint region boundary
            # Find closest breakpoint to h
            close_break = np.argmin(np.abs(self.area_fit['h_break'] - h))

            # If hhat is beyond the maximum observed h, map point to final breakpoint
            if close_break == 3:
                
                # Retrieve final region fit
                p0=self.area_fit['fit_coeffs'][1,close_break-1,0]  #intercept
                p1=self.area_fit['fit_coeffs'][0,close_break-1,0]  #slope
                
            else:
            
                # Retrieve region fit
                p0=self.area_fit['fit_coeffs'][1,close_break,0]  #intercept
                p1=self.area_fit['fit_coeffs'][0,close_break,0]  #slope
            
            # Map point to intersection of subdomain fit and breakpoint
            hhat = self.area_fit['h_break'][close_break]
            what = p0 + p1  * hhat
################################################################################     
            
        return hhat,what
                    
            
    def MapPointToSubDomain(self,sd,hobs,wobs):
 
        p0=self.area_fit['fit_coeffs'][1,sd,0]  #intercept
        p1=self.area_fit['fit_coeffs'][0,sd,0]  #slope

        # use Fuller 1.3.17
        vhat=wobs-p0-p1*hobs
        suv=-p1*self.sigh**2 #could add a rho term here
        svv=self.sigw**2 + p1**2 * self.sigh**2 #could add a rho term here

        hhatsd=hobs-suv/svv*vhat
        whatsd=p0+p1*hhatsd

        return hhatsd,whatsd

    def plotHW(self,plottitle=[]):

        #plt.style.use('tableau-colorblind10')

        fig,ax = plt.subplots()
        
        if hasattr(self,'area_fit'):

            for sd in range(3):
                htest=linspace(self.area_fit['h_break'][sd],self.area_fit['h_break'][sd+1],10)
                wtest=self.area_fit['fit_coeffs'][0,sd,0]*htest+self.area_fit['fit_coeffs'][1,sd,0]
                #plt.plot(htest,wtest,color='C0')
                plt.plot(htest,wtest,color='tab:orange')
        
        if self.ConstrainHWSwitch:
            for i in range(self.D.nt):
                ax.plot([self.hobs[i],self.h[0,i]],[self.wobs[i],self.w[0,i]],color='grey')
            ax.scatter(self.hobs,self.wobs,marker='o')   
            ax.scatter(self.h[0,:],self.w[0,:],marker='o')   
        else: 
            ax.scatter(self.h[0,:],self.w[0,:],marker='o')   


        if bool(plottitle):
            plt.title(plottitle)
        plt.xlabel('WSE, m')
        plt.ylabel('Width, m')      
        plt.show() 
        
    def plotdA(self):
        fig,ax = plt.subplots()
        ax.plot(self.D.t.T,self.dA[0,:])        
            
        plt.title('dA timeseries')
        plt.xlabel('Time, days')
        plt.ylabel('dA, m^2')      
        plt.show()       
        
    def plotHdA(self):
        fig,ax = plt.subplots()
        
        ax.scatter(self.h[0,:],self.dA[0,:],marker='o')   
            
        plt.title('dA vs WSE for first reach')
        plt.xlabel('WSE, m')
        plt.ylabel('dA, m')      
        plt.show()         

    def FitLOC(self,x,y):
        #references from Statistical Methods in Water Resources, by Helsel &
        #Hirsch, 1992. 

        sx=std(x)
        sy=std(y)

        mx=mean(x)
        my=mean(y)

        n=len(x)

        r=1/(n-1) * sum( (x-mx)/sx * (y-my)/sy ) # 8.6: Pearson's r

        b1=r*sy/sx #text below 10.7
        b1prime=1/r*sy/sx #text below 10.9

        b1doubleprime=sqrt(b1*b1prime) #slope: text above 10.10

        b0doubleprime=my-b1doubleprime*mx #intercept: comparing 10.10 with 10.9

        return b1doubleprime, b0doubleprime

    def FitEIV(self,x,y):
        #this is derived from fuller, for the ratio of variances model 1.3.7

        #compute sample variances and covariance
        mXX=var(x)
        mYY=var(y)
        Sigma=cov(x,y)
        mXY=Sigma[0,1]
 
        #this option has delta set to 1
        #beta1hat=((mYY-mXX)+( (mYY-mXX)**2 + 4*mXY**2   )**0.5 ) / (2*mXY)
        
        #this option lets you specify delta
        delta=1.0
        beta1hat=((mYY-delta*mXX)+( (mYY-delta*mXX)**2 + 4*delta*mXY**2   )**0.5 ) / (2*mXY)

        beta0hat=mean(y)-beta1hat*mean(x)

        return beta1hat, beta0hat

    def CalcAreaFits(self,r=0):

        warnings.filterwarnings("ignore", message="delta_grad == 0.0. Check if the approximated function is linear.")

        # this computes the SWOT-like height-width fit

 	# r : reach ID

        # outer level parameter vector:
        # po = Hb0,Hb1 i.e. WSE breakpoint 0, then WSE breakpoint 1
        # inner level parameter vector:
        # pi = p00, p01, p10, p11, p20,p21 i.e. p[domain 0][coefficient 0], p[domain 0][coefficient 1], p[domain 1][coefficient 0],...

        #0 check uncertainties
        if self.sigw<0:
             self.sigw=10 
        igoodh=np.logical_not(np.isnan(self.h[r,:]))
        igoodw=np.logical_not(np.isnan(self.w[r,:]))
        igoodhw=np.logical_and(igoodh,igoodw)

        if not any(igoodhw):
            print('No good data. Not computing height-width fits.')
            return

        #1 choose initial parameters for outer loop

        WSEmin=min(self.h[r,igoodhw])
        WSEmax=max(self.h[r,igoodhw])
        WSErange=WSEmax-WSEmin
        WSErange=WSEmax-WSEmin
        init_params_outer=[WSEmin+WSErange/3, WSEmin+2*WSErange/3]

        #2 compute a solution where we set the breakpoints at 1/3 of the way through the domain
        ReturnSolution=True
        Jset,p_inner_set=SSE_outer(init_params_outer,self.h[r,igoodhw],self.w[r,igoodhw],ReturnSolution,self.sigh,self.sigw,self.Verbose)
        
################################################################################
        # JW EDITS: In some cases, initial fit is extremely poor or negative

        # When slope terms of subregions > 10000 or negative,, instead use rectangular fit
        if p_inner_set[0] > 10000 or p_inner_set[2] > 10000 or p_inner_set[4] > 10000 or\
            p_inner_set[0] < 0 or p_inner_set[2] < 0 or p_inner_set[4] < 0: 
            print('Implausible set fit. Implementing rectangular fit.')
            
            # Find median of widths
            med_width = np.nanmedian(self.w[r,igoodhw])
            
            # Set p_inner_set parameters to rectangular fit at median width
            p_inner_set[0] = 0  # slope R1
            p_inner_set[1] = med_width  # intercept R1
            p_inner_set[2] = 0  # slope R2
            p_inner_set[3] = med_width  # intercept R2
            p_inner_set[4] = 0  # slope R3
            p_inner_set[5] = med_width  # intercept R3
            
            # Enforce rectangular fit due to implausible set fit (Jset = -1)
            Jset = -1
            Jsimple = 0
            # Set placeholder variables for p2
            p2 = [0, 0, 0]
################################################################################
            
        if self.Verbose:
            print('height-width fit for set breakpoints')
            plot3SDfit(self.h[r,:],self.w[r,:],p_inner_set,init_params_outer)

        #3 optimize both inner and outer loop simultaneously

        #3.1 parameter bounds
        nparams_outer=len(init_params_outer)
        lb=zeros(nparams_outer,)
        ub=zeros(nparams_outer,)

        lb[0]=WSEmin+WSErange*0.1
        ub[0]=WSEmin+WSErange*0.9
        lb[1]=WSEmin+WSErange*0.1
        ub[1]=WSEmin+WSErange*0.9

        param_bounds_outer=optimize.Bounds(lb,ub)

        #3.2 constrain breakpoints to be monotonic
        A=array([[1,-1]])
        constraint2=optimize.LinearConstraint(A,-inf,-0.1)    

        #3.3 nested solution to three-subdomain fit
        if self.CalcAreaFitOpt == 2:
            #3.3.1 optimize breakpoints
            ReturnSolution=False
            res = optimize.minimize(fun=SSE_outer,
                    x0=init_params_outer,
                    args=(self.h[r,:],self.w[r,:],ReturnSolution,self.sigh,self.sigw,self.Verbose),
                    bounds=param_bounds_outer,
                    method='trust-constr',    
                    constraints=constraint2,
                    options={'disp':self.Verbose,'maxiter':1e3,'verbose':0})

            params_outer_hat=res.x

            #3.3.2 compute optimal fits for optimal breakpoints
            ReturnSolution=True
            [Jnest,params_inner_nest]=SSE_outer(params_outer_hat,self.h[r,:],self.w[r,:],ReturnSolution,self.sigh,self.sigw,self.Verbose)

            # if self.Verbose:
            #     print('height-width fit for nested optimization')
            #     plot3SDfit(self.h[r,:],self.w[r,:],params_inner_nest,params_outer_hat)

        #3.3.3 determine whether to use optimal breakpoint solution or equal-spaced breakpoints 
        if self.CalcAreaFitOpt == 2  and(res.success or (Jnest<Jset)):
             print('nested optimiztion sucess:',res.success)
             print('nested objective:',Jnest)
             print('set objective function:',Jset)
             print('using nested solution')
             self.Hbp=params_outer_hat
             self.HWparams=params_inner_nest
        else:
             self.Hbp=init_params_outer
             self.HWparams= p_inner_set

        #3.4 compute simple optimal breakpoints, then compute fits
        if self.CalcAreaFitOpt == 3:
            
            #3.4.1 optimize breakpoints 
            def piecewise_linear2(x, x0, y0, x1, k1, k2, k3):
                return piecewise(x, [x < x0, ((x>=x0)&(x<x1)), x>=x1], \
                    [lambda x:k1*x + y0-k1*x0, lambda x:k2*x + y0-k2*x0, lambda x:k3*x + k2*x1+y0-k2*x0-k3*x1])  
                

            # JW EDIT: In some cases, the maximum function evaluations is exceeded
            # If rectangular fit imposed during set fit (Jset = -1), don't implement simple fit
            if Jset != -1:
                 
                try:
                    p2 , e2 = optimize.curve_fit(piecewise_linear2, self.h[r,igoodhw], self.w[r,igoodhw],\
                         bounds=([lb[0],-inf,lb[0],0,0,0],[ub[0],inf,ub[0],inf,inf,inf]),\
                         p0=[init_params_outer[0],mean(self.w[r,igoodhw]),init_params_outer[1],0,0,0],\
                         maxfev=1000)
                        
                    #this specifies the two WSE breakpoints
                    params_outer_hat=[p2[0],p2[2]]
        
                    #3.4.2 compute parameters
                    ReturnSolution=True
                    Jsimple,p_inner_simple=SSE_outer(params_outer_hat,self.h[r,igoodhw],self.w[r,igoodhw],ReturnSolution,self.sigh,self.sigw,self.Verbose)
                           
                    # JW EDITS: In some cases, simple fit is extremely poor or negative
                    # When slope terms of subregions > 10,000 or negative, instead use set fit
                    if p_inner_simple[0] > 10000 or p_inner_simple[2] > 10000 or p_inner_simple[4] > 10000 or\
                        p_inner_set[0] < 0 or p_inner_set[2] < 0 or p_inner_set[4] < 0: 
                        print('Implausible simple fit. Implementing set fit')
                        
                        # Enforce set fit due to implausible simple fit (Jset = -2)
                        Jset = -2
                              
                # JW EDITS: In some cases, simple fit is not close to observed points
                # Check that observations are within reasonable distance of constrainted points
                        
                except RuntimeError as e:
                   print("Optimization failed, using set breakpoint fit.")
                   # Enforce set fit due to failed optimization (Jset = -3)
                   Jset = -3
                   Jsimple = -2
                   # Set placeholder variables for p2
                   p2 = [0, 0, 0]
                

             # if self.Verbose:
             #     print('height-width fit for simple optimized breakpoints')
             #     plot3SDfit(self.h[r,:],self.w[r,:],p_inner_simple,params_outer_hat)
 
             #3.4.3 determine whether to use optimal breakpoint solution or equal-spaced breakpoints 
             #if self.Verbose:
                  #print('simple objective:',Jsimple)
                  #print('set objective function:',Jset)
             # if  Jsimple<Jset or p2[0]>p2[2]:
                     
             #      if self.Verbose:
             #           if p2[0]>p2[2]:
             #                print('p2[0]>p2[2]. p2[0]=',p2[0],'p2[2]=',p2[2])
             #           print('using simple solution')
             #      if p2[0]>p2[2]:
             #           print('p2[0]>p2[2]. p2[0]=',p2[0],'p2[2]=',p2[2])

             #      self.Hbp=params_outer_hat
             #      self.HWparams=p_inner_simple
             # else:
             #      if self.Verbose:
             #           print('using set breakpoints ')
                                        
             #      self.Hbp=init_params_outer
             #      self.HWparams= p_inner_set

################################################################################                
        # JW EDITS: Fix inequality to ensure correct fit is used
        if  Jset<Jsimple or p2[0]>p2[2]:
               
            if self.Verbose:
                  if p2[0]>p2[2]:
                      print('p2[0]>p2[2]. p2[0]=',p2[0],'p2[2]=',p2[2])
                  print('using set breakpoint fit')
            self.Hbp=init_params_outer
            self.HWparams= p_inner_set
            self.fit_method = 'set'

        else:
            if self.Verbose:
                print('using simple solution ')
                                 
            self.Hbp=params_outer_hat
            self.HWparams=p_inner_simple
            self.fit_method = 'simple'
            
        if Jset == -1:
            self.fit_method = 'rectangular'
################################################################################      

        #4 pack up fit parameter data matching swot-format 
        #4.0 initialize
        area_fit={}
        #4.1 set the dataset stats
        area_fit['h_variance']=array(var(self.h[r,igoodhw]))
        area_fit['w_variance']=array(var(self.w[r,igoodhw]))
        hwcov=cov(self.w[r,igoodhw],self.h[r,igoodhw])
        area_fit['hw_covariance']=hwcov[0,1]
        area_fit['med_flow_area']=array(0.) #this value estimated as described below 
        area_fit['h_err_stdev']=array(self.sigh)
        area_fit['w_err_stdev']=array(self.sigw)
        area_fit['h_w_nobs']=array(self.D.nt)

        #4.2 set fit_coeffs aka parameters aka coefficients - translate to SWOT L2 style format
        # pi = p00, p01, p10, p11, p20,p21 i.e. p[domain 0][coefficient 0], p[domain 0][coefficient 1], p[domain 1][coefficient 0],...
        nsd=3
        ncoef=2
        area_fit['fit_coeffs']=zeros((ncoef,nsd,1))
        for sd in range(nsd):
            for coef in range(ncoef):
                param_indx=sd*ncoef+coef
                area_fit['fit_coeffs'][coef,sd] = self.HWparams[param_indx]

        #4.3 set h_break
        area_fit['h_break']=zeros((4,1))
################################################################################
        # JW: Change to nanmin to allow for nan values for fail to constrain pts1
        area_fit['h_break'][0]=np.nanmin(self.h[r,:])  
################################################################################        
        area_fit['h_break'][1]=self.Hbp[0]
        area_fit['h_break'][2]=self.Hbp[1]
################################################################################             
        # JW: Change to nanmax to allow for nan values for fail to constrain pts
        area_fit['h_break'][3]=np.nanmax(self.h[r,:])
################################################################################     

        #4.4 set w_break... though i do not think this get used so just initializing for now
        area_fit['w_break']=zeros((4,1))

        #4.5 calculate cross-sectional area at median value of H
        # a bit confusing, but we are centering the dA on the median H. so to get a dA value that
        # coresponds to Hbar, we set dA_hbar to zero, then evaluate the area fit at a value of 
        # Hbar. That returns the area value at median H that we use going forward
        Hbar=nanmedian(self.h[r,:])
        wbar=nanmedian(self.w[r,:])

        dA_Hbar,hhat,what,dAunc=area(Hbar, wbar, area_fit)

        area_fit['med_flow_area']=dA_Hbar

        #4.6 save fit data
        self.area_fit=area_fit

        #if self.Verbose:
            #print('area fit parameters=',self.area_fit)

        return 

def ChooseInitParamsInner(h,w):
    #function to choose initial parameters describing SWOT-like height-width fit

    p1SD=polyfit(h,w,1) #slope and intercept for one sub-domain    

    ############################################################################               
    # JW EDITS: Polyfit can produce yintercept values that are extremely poor
    # initial guesses for optimization
    # # If any slope is negative, fit a flat slope through median
    if p1SD[0] < 0:
    
        med_w = np.nanmedian(w)
        init_params_inner=[0,med_w,0,med_w,0,med_w]
        
    else:

        init_params_inner=[p1SD[0],p1SD[1],p1SD[0],p1SD[1],p1SD[0],p1SD[1]]

    ############################################################################   
    
    nparams_inner=len(init_params_inner)
    
    return init_params_inner,nparams_inner

def SetInnerParamBounds(nparams):
    #function to set initial parameter bounds describing SWOT-like height-width fit
    
    lb=zeros(nparams,)
    ub=zeros(nparams,)
      
    # slope values are 0,2,4. intercept values are 1,3,5
        
    # slope lower bound is zero, but upper bound is inf
    ub[0]=inf
    ub[2]=inf
    ub[4]=inf
    
    lb[0]=0 
    lb[2]=0
    lb[4]=0
    
    # intercept does not have bounds    
    lb[1]=-inf
    lb[3]=-inf
    lb[5]=-inf
    
    ub[1]=inf
    ub[3]=inf    
    ub[5]=inf
    
    return lb,ub

# define outer objective function, with inner objective function nested within
def SSE_outer(param_outer,h,w,ReturnSolution,sigh,sigw,Verbose):
    
    [init_params_inner,nparams_inner]=ChooseInitParamsInner(h,w)
    
    [lb,ub]=SetInnerParamBounds(nparams_inner)

    param_bounds_inner=optimize.Bounds(lb,ub)

    def SSE_inner(inner_params,xbreak,h,w,sigh,sigw):            
        
        i0=h<xbreak[0]                
        J0=(sigw**2 + inner_params[0]**2 * sigh**2)**-1*sum((h[i0]*inner_params[0]+inner_params[1]-w[i0])**2 ) #1.3.20 in Fuller
        i1=(h>=xbreak[0]) & (h<xbreak[1])
        J1=(sigw**2 + inner_params[2]**2 * sigh**2)**-1*sum((h[i1]*inner_params[2]+inner_params[3]-w[i1])**2 )    
        i2=h>=xbreak[1]
        J2=(sigw**2 + inner_params[4]**2 * sigh**2)**-1*sum((h[i2]*inner_params[4]+inner_params[5]-w[i2])**2 )            
        
        J=J0+J1+J2 

        return J
 
    def cons0_f(x):        
        return x[0]*param_outer[0]+x[1]-x[2]*param_outer[0]-x[3] #this constraint requies this function to be equal to zero
    def cons1_f(x):        
        return x[2]*param_outer[1]+x[3]-x[4]*param_outer[1]-x[5] #this constraint requies this function to be equal to zero

    constraint0=optimize.NonlinearConstraint(cons0_f,0,0)
    constraint1=optimize.NonlinearConstraint(cons1_f,0,0)
        
    constraints=[constraint0,constraint1]    

    ShowDetailedOutput=Verbose
    if not ReturnSolution:
        ShowDetailedOutput=False

    res = optimize.minimize(fun=SSE_inner,
                    x0=init_params_inner,
                    args=(param_outer,h,w,sigh,sigw),
                    bounds=param_bounds_inner,
                    method='trust-constr',
                    constraints=constraints,
                    #options={'disp':ShowDetailedOutput,'maxiter':1e3,'verbose':0})    
                    options={'disp':False,'maxiter':1e3,'verbose':0})    

    if ReturnSolution:    
        return res.fun,res.x
    else:
        return res.fun
    

def plot3SDfit(h,w,params_inner,params_outer):
    fig,ax = plt.subplots()
    ax.scatter(h,w,marker='o')
    plt.title('WSE vs width ')
    plt.xlabel('WSE, m')
    plt.ylabel('Width, m')

    htest0=linspace(min(h),params_outer[0],10 )
    wtest0=params_inner[0]*htest0+params_inner[1]
    htest1=linspace(params_outer[0],params_outer[1],10)
    wtest1= params_inner[2]*htest1+params_inner[3]
    htest2=linspace(params_outer[1],max(h),10)
    wtest2= params_inner[4]*htest2+params_inner[5]

    plt.plot(htest0,wtest0,htest1,wtest1,htest2,wtest2)

    plt.show()
    return

# the area and estimate_height functions below are copy and pasted from discharge.py 
# in the offline-discharge-data-product-creation repo. february 3, 2022 -mike

def area(observed_height, observed_width, area_fits):
    """
    Provides a nicer interface for _area wrapping up the unpacking of prior
    db area_fits into CalculatedAEIV.m inputs.

    observed_height - swot observed height for this reach
    observed_width - swot observed width for this reach
    area_fits - dictionary of things extracted from prior DB
    """
    height_breakpoints = np.squeeze(area_fits['h_break'])
    poly_fits = [
        np.squeeze(area_fits['fit_coeffs'])[:, 0],
        np.squeeze(area_fits['fit_coeffs'])[:, 1],
        np.squeeze(area_fits['fit_coeffs'])[:, 2]]

    area_median_flow = np.squeeze(area_fits['med_flow_area'])

    fit_width_std = np.squeeze(area_fits['w_err_stdev'])
    fit_height_std = np.squeeze(area_fits['h_err_stdev'])

    cov_height_width = np.zeros([2, 2])
    cov_height_width[0, 0] = np.squeeze(area_fits['w_variance'])
    cov_height_width[0, 1] = np.squeeze(area_fits['hw_covariance'])
    cov_height_width[1, 0] = cov_height_width[0, 1]
    cov_height_width[1, 1] = np.squeeze(area_fits['h_variance'])
    num_obs = np.squeeze(area_fits['h_w_nobs'])

    return _area(
        observed_height, observed_width, height_breakpoints, poly_fits,
        area_median_flow, fit_width_std**2, fit_height_std**2,
        cov_height_width, num_obs)

def _area(
    observed_height, observed_width, height_breakpoints, poly_fits,
    area_median_flow, fit_width_var, fit_height_var, cov_height_width,
    num_obs):
    """
    Computes cross-sectional area from fit, based on CalculatedAEIV.m at
    https://github.com/mikedurand/SWOTAprimeCalcs

    observed_height - swot observed height for this reach
    observed_width - swot observed width for this reach
    height_breakpoints - boundaries for fits in height
    poly_fits - polynominal coeffs for the fits
    area_median_flow - cross-sectional area at median flow
    fit_width_var - width error std**2
    fit_height_var - height error std**2
    cov_height_width - covariance matrix for width / height
    """
    poly_ints = np.array([np.polyint(item) for item in poly_fits])

    height_fits_ll = height_breakpoints[0:-1]
    height_fits_ul = height_breakpoints[1:]

    ifit = np.argwhere(np.logical_and(
        observed_height >= height_fits_ll,
        observed_height < height_fits_ul))

    low_height_snr = (
        cov_height_width[1, 1] - fit_height_var)/fit_height_var < 2

    if ifit.size == 0:
        observed_height_hat = np.nan
        observed_width_hat = observed_width
        if observed_height > height_breakpoints.max():
            delta_area_hat = (
                np.polyval(poly_ints[-1], height_breakpoints[-1]) -
                np.polyval(poly_ints[-1], height_breakpoints[-2]) +
                area_median_flow)
            dAunc = np.sqrt(
                fit_height_var*observed_width**2 +
                2*fit_width_var*(observed_height-height_breakpoints[-1])**2)

        else:
            delta_area_hat = (
                - area_median_flow - ((height_breakpoints[0]-observed_height)
                * (observed_width + poly_fits[0][0]*height_breakpoints[0]
                + poly_fits[0][1])/2))
            dAunc = np.sqrt(
                fit_height_var*observed_width**2 +
                2*fit_width_var*(observed_height-height_breakpoints[0])**2)

    else:
        ifit = ifit[0][0]
        if low_height_snr:
            observed_height_hat = observed_height
        else:
            observed_height_hat = estimate_height(
                observed_width, observed_height, poly_fits[ifit],
                fit_width_var, fit_height_var)

        ifit_hat = np.argwhere(np.logical_and(
            observed_height_hat >= height_fits_ll,
            observed_height_hat < height_fits_ul))

        if ifit_hat.size > 0:
            ifit = ifit_hat[0][0]
            observed_height_hat = estimate_height(
                observed_width, observed_height, poly_fits[ifit],
                fit_width_var, fit_height_var)

        if low_height_snr:
            observed_width_hat = observed_width
        else:
            observed_width_hat = np.polyval(
                poly_fits[ifit], observed_height_hat)

        delta_area_hat = 0
        for poly_int, height_ll, height_ul in zip(
            poly_ints[:ifit+1], height_fits_ll[:ifit+1],
            height_fits_ul[:ifit+1]):

            delta_area_hat += (
                np.polyval(poly_int, np.min([observed_height_hat, height_ul]))
                - np.polyval(poly_int, height_ll))

        delta_area_hat -= area_median_flow

        if poly_fits[ifit][0] == 0:
            dAunc = poly_fits[ifit][1] * np.sqrt(fit_height_var)
        else:
            mu = (np.sqrt(
                poly_fits[ifit][0]/2) *
                (observed_height_hat - height_fits_ul[ifit]) + np.polyval(
                poly_fits[ifit], height_fits_ul[ifit]) / np.sqrt(
                2 * poly_fits[ifit][0]))
            sigma = np.sqrt(poly_fits[ifit][0]/2) * np.sqrt(fit_height_var)
            dAunc = np.sqrt(4*mu**2*sigma**2 + 2*sigma**4);

    return delta_area_hat, observed_width_hat, observed_height_hat, dAunc

def estimate_height(observed_width, observed_height, poly_fit, fit_width_var,
                    fit_height_var):
    """Estimates optimal height using error in variables approach"""
    #note this implements eqn. 1.3.17 in Fuller, assuming sigma_eu=0
    sigma_vv = fit_width_var + poly_fit[0]**2 * fit_height_var
    sigma_uv = -poly_fit[0] * fit_height_var
    v = observed_width - poly_fit[1] - poly_fit[0] * observed_height
    return observed_height - v * sigma_uv/sigma_vv
