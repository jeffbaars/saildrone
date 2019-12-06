#!/usr/bin/python
import os, sys, glob, re, math
import numpy as np
from collections import defaultdict
import pickle
from utils_date import *
from utils_ghcnd_obs import *

dtfmt = "%Y%m%d%H"

mm2in           = 0.0393700787
min_season_days = 85
std_lapse       = 0.0065  #-- std. atmos. lapse rate
mvc             = -9999.0

vars_sb_mod_dict = {
    'TMP_2maboveground'   : 't', 
    'DPT_2maboveground'   : 'td', 
    'PRMSL_meansealevel'  : 'slp',
    'UGRD_10maboveground' : 'u',
    'VGRD_10maboveground' : 'v'    
    }
vars_sail_mod_dict = {
    'TMP_2maboveground'   : 'TEMP_AIR_MEAN', 
    'DPT_2maboveground'   : 'TD_MEAN',
    'PRMSL_meansealevel'  : 'BARO_PRES_MEAN',
    'UGRD_10maboveground' : 'UWND_MEAN',
    'VGRD_10maboveground' : 'VWND_MEAN',
    'TMP_surface'         : 'TEMP_CTD_RBR_MEAN'
    }

#---------------------------------------------------------------------------
# Get model - obs differences, interpolating from sent-in model grid to
# sent-in obs points.
#---------------------------------------------------------------------------
def get_diffs(stns, dat_obs, dat_model, vars_model, lat_model, lon_model, \
              model, sailorsb):

    if sailorsb == 'sail':
        vars_mod_dict = vars_sail_mod_dict
    else:
        vars_mod_dict = vars_sb_mod_dict
        
    diffs  = {}
    modpts = {}    
    for s in range(len(stns)):
        stn = stns[s]
        if sailorsb == 'sail':
            lat_c = dat_obs[stn]['latitude']
            lon_c = dat_obs[stn]['longitude'] + 360
        else:
            lat_c = dat_obs[stn,'latitude']
            lon_c = dat_obs[stn,'longitude'] + 360

        diffs[stn,'latitude'] = lat_c
        diffs[stn,'longitude'] = lon_c
        for v in range(len(vars_model)):
            var_mod = vars_model[v]
            if not var_mod in vars_mod_dict:
                continue
            if sailorsb == 'sail':
                obs_c = dat_obs[stn][vars_mod_dict[var_mod]]
            elif sailorsb == 'sb':
                obs_c = dat_obs[stn,vars_mod_dict[var_mod]]

            modpt_c = bilinear_interpolate(lat_model, lon_model, \
                                           dat_model[var_mod], lat_c, lon_c, 0)
            if sailorsb == 'sail':
                if var_mod == 'TMP_2maboveground' or \
                   var_mod == 'DPT_2maboveground' or \
                   var_mod == 'TMP_surface':
                    obs_c = obs_c + 273.15
                elif var_mod == 'PRMSL_meansealevel':
                    obs_c = obs_c * 100.0                
                
            diffs[stn,var_mod] = modpt_c - obs_c
            modpts[stn,var_mod] = modpt_c
            print stn, var_mod, modpt_c, obs_c, modpt_c - obs_c
            
    return diffs, modpts

#---------------------------------------------------------------------------
# Get model - obs differences, interpolating from sent-in model grid to
# sent-in obs points.
#---------------------------------------------------------------------------
def get_diffs_ts(stns, dt, dat_obs, dat_model, vars_model, \
                 lat_model, lon_model, model, sailorsb, diffs, modpts):

    if sailorsb == 'sail':
        vars_mod_dict = vars_sail_mod_dict
    else:
        vars_mod_dict = vars_sb_mod_dict
        
#    diffs  = {}
#    modpts = {}    
    for s in range(len(stns)):
        stn = stns[s]
        if sailorsb == 'sail':
            if dat_obs[stn,dt] == dat_obs[stn,dt]:
                lat_c = dat_obs[stn,dt]['latitude']
                lon_c = dat_obs[stn,dt]['longitude'] + 360
            else:
                continue
        else:
            lat_c = dat_obs[stn,dt,'latitude']
            lon_c = dat_obs[stn,dt,'longitude'] + 360

        diffs[stn,dt,'latitude'] = lat_c
        diffs[stn,dt,'longitude'] = lon_c
        for v in range(len(vars_model)):
            var_mod = vars_model[v]
            if not var_mod in vars_mod_dict:
                continue
            if sailorsb == 'sail':
                obs_c = dat_obs[stn,dt][vars_mod_dict[var_mod]]
            elif sailorsb == 'sb':
                obs_c = dat_obs[stn,dt,vars_mod_dict[var_mod]]

            try:
                modpt_c = bilinear_interpolate(lat_model, lon_model, \
                                               dat_model[var_mod], \
                                               lat_c, lon_c, 0)
            except:
                modpt_c = np.nan
                
            if sailorsb == 'sail':
                if var_mod == 'TMP_2maboveground' or \
                   var_mod == 'DPT_2maboveground' or \
                   var_mod == 'TMP_surface':
                    obs_c = obs_c + 273.15
                elif var_mod == 'PRMSL_meansealevel':
                    obs_c = obs_c * 100.0                
                
            diffs[stn,dt,var_mod] = modpt_c - obs_c
            modpts[stn,dt,var_mod] = modpt_c
            print dt, stn, var_mod, modpt_c, obs_c, modpt_c - obs_c
            
    return diffs, modpts

#---------------------------------------------------------------------------
# Interpolate from a sent-in grid to a sent in lat/lon point.
#---------------------------------------------------------------------------
def bilinear_interpolate(latgrid, longrid, datagrid, latpt, lonpt, deb):

    totdiff = abs(latgrid - latpt) + abs(longrid - lonpt)
    (i,j) = np.unravel_index(totdiff.argmin(), totdiff.shape)

    #--- Get lat/lon box in which latpt,lonpt resides.
    iif = np.nan
    jjf = np.nan    
    if (latpt >= latgrid[i,j] and lonpt >= longrid[i,j]):
        iif = i
        jjf = j
    elif (latpt < latgrid[i,j] and lonpt < longrid[i,j]):
        iif = i-1
        jjf = j-1
    elif (latpt >= latgrid[i,j] and lonpt < longrid[i,j]):
        iif = i-1
        jjf = j
    elif (latpt < latgrid[i,j] and lonpt >= longrid[i,j]):
        iif = i
        jjf = j-1

    (nx, ny) = np.shape(latgrid)

    if (deb == 1):
        print 'nx, ny  = ', nx, ny
        print 'iif,jjf = ', iif,jjf
        print 'latgrid[iif+1,jjf] = ', latgrid[iif+1,jjf]
        print 'latgrid[iif,jjf]   = ', latgrid[iif,jjf]

    if iif != iif or jjf != jjf:
        return mvc
    if (iif >= (nx-1) or jjf >= (ny-1) or iif < 0 or jjf < 0):
        return mvc

    #--- Do bilinear interpolation to latpt,lonpt.
    dlat  = latgrid[iif,jjf+1] - latgrid[iif,jjf]
    dlon  = longrid[iif+1,jjf] - longrid[iif,jjf]
    dslat = latgrid[iif,jjf+1] - latpt
    dslon = longrid[iif+1,jjf] - lonpt

    wrgt = 1 - (dslon/dlon)
    wup  = 1 - (dslat/dlat)

    vll = datagrid[iif,jjf]
    vlr = datagrid[iif,jjf+1]
    vul = datagrid[iif+1,jjf]
    vur = datagrid[iif+1,jjf+1]

    if (deb > 1):
        print 'll lat, lon, val = ', latgrid[iif,jjf], longrid[iif,jjf], vll
        print 'lr lat, lon, val = ', latgrid[iif+1,jjf], longrid[iif+1,jjf], vlr
        print 'ur lat, lon, val = ', latgrid[iif+1,jjf+1], longrid[iif+1,jjf+1],vur
        print 'ul lat, lon, val = ', latgrid[iif,jjf+1], longrid[iif,jjf+1], vul
        print 'latpt, lonpt = ', latpt, lonpt
        
        print 'vll = ', vll
        print 'vlr = ', vlr
        print 'vul = ', vul
        print 'vur = ', vur

    datout = (1-wrgt) * ((1-wup) * vll + wup * vul) + \
        (wrgt) * ((1-wup) * vlr + wup * vur)

#    if (deb == 1):
#        print 'datout = ', datout
#        sys.exit()
#    if (datout == 0.0):
#        print 'nx, ny  = ', nx, ny
#        print 'iif,jjf = ', iif,jjf
#        print 'latgrid[iif+1,jjf] = ', latgrid[iif+1,jjf]
#        print 'latgrid[iif,jjf]   = ', latgrid[iif,jjf]
#        
#        print 'll lat, lon, val = ', latgrid[iif,jjf], longrid[iif,jjf], vll
#        print 'lr lat, lon, val = ', latgrid[iif+1,jjf], longrid[iif+1,jjf], vl#r
#        print 'ur lat, lon, val = ', latgrid[iif+1,jjf+1], longrid[iif+1,jjf+1],vur
#        print 'ul lat, lon, val = ', latgrid[iif,jjf+1], longrid[iif,jjf+1], vu#l
#        print 'latpt, lonpt = ', latpt, lonpt
#        
#        print 'vll = ', vll
#        print 'vlr = ', vlr
#        print 'vul = ', vul
#        print 'vur = ', vur
#
#        sys.exit()

    return datout

#----------------------------------------------------------------------------
# Add data to sums, max's and min's arrays.
#----------------------------------------------------------------------------
def get_season_summaxmin(dat_c, mod, stn, season, yyyyin, month, ndays, \
                         out_sum, out_max, out_min):

    #--- Look out for cases where data is NaN (e.g. the 31st of June) and
    #--- do nothing (return) in those cases.
    if np.isnan(dat_c):
        return ndays, out_sum, out_max, out_min
        
    #--- Put December winter data into next year's winter-- naming
    #--- winters by their Jan/Feb year rather than their Dec year.
    if month == '12':
        yyyy = str(int(yyyyin) + 1)
    else:
        yyyy = yyyyin
        
    #--- Count number of days for this season and year.
    if (season+yyyy) in ndays:
        ndays[season+yyyy] += 1
    else:
        ndays[season+yyyy] = 1

    key = (season,mod,stn,yyyy)

    #--- Get sum of sent in data.
    if key in out_sum:
        out_sum[key] = out_sum[key] + dat_c
    else:
        out_sum[key] = dat_c

    #--- Get maximum.
    if key in out_max:
        if dat_c > out_max[key]:
            out_max[key] = dat_c
    else:
        out_max[key] = dat_c
            
    #--- Get minimum.
    if key in out_min:
        if dat_c < out_min[key]:
            out_min[key] = dat_c
    else:
        out_min[key] = dat_c

    return ndays, out_sum, out_max, out_min
