#!/usr/bin/python
import os, sys, glob, re, math
import numpy as np
from collections import defaultdict
from netCDF4 import Dataset as NetCDFFile
import pickle
from utils_date import *
from utils_stats import *
from utils_ghcnd_obs import *
import csv

mvc_rawins = -888888.0
ms2knots =  1.94384
pid = 0.0175;

#---------------------------------------------------------------------------
# Load geo_em file.
#---------------------------------------------------------------------------
def load_geo_em(geo_em):
    nc = NetCDFFile(geo_em, 'r')
    lat = nc.variables['XLAT_M'][0,:,:]
    lon = nc.variables['XLONG_M'][0,:,:]
    hgt = nc.variables['HGT_M'][0,:,:]    
    lat = np.transpose(lat)
    lon = np.transpose(lon)
    hgt = np.transpose(hgt)
    clats = nc.corner_lats
    clons = nc.corner_lons
    nc.close()
    return lat, lon, hgt, clats, clons

#---------------------------------------------------------------------------
# Load (GFS) model data file.
#---------------------------------------------------------------------------
def load_model_data(mfile, vars):
    dataout = {}
    nc = NetCDFFile(mfile, 'r')
    lat = nc.variables['latitude'][:]
    lon = nc.variables['longitude'][:]
    for v in range(len(vars)):
        var = vars[v]
        dat_tmp = nc.variables[var][0,:,:]
        dataout[var] = np.transpose(dat_tmp)
    nc.close()

    #--- Create 2-D lat/lon grids.
    lon2d, lat2d = np.meshgrid(lon, lat, indexing='ij')

    #--- Get spd and dir from u and v.
    wdirs, spds = uv_to_dirspd(dataout['UGRD_10maboveground'], \
                               dataout['VGRD_10maboveground'])
    dataout['SPD_10maboveground'] = spds
    dataout['DIR_10maboveground'] = wdirs

    return dataout, lat2d, lon2d

#---------------------------------------------------------------------------
# Speed and direction to u/v. 
#---------------------------------------------------------------------------
def dirspd_to_uv(wdir, spd):
    u = spd * np.cos(pid * (90.0 + wdir))
    v = -spd * np.sin(pid * (90.0 + wdir))
    return u, v

#---------------------------------------------------------------------------
# u and v to direction and speed.  Allows for 2-D u and v grids.
#---------------------------------------------------------------------------
def uv_to_dirspd(u, v):
    spd = np.sqrt(np.add(np.multiply(u,u), np.multiply(v,v)))
    wdir = (np.arctan2(1,0) - np.arctan2(v, u)) / pid
    wdir = np.mod(wdir + 900, 360)
    return wdir, spd

#---------------------------------------------------------------------------
# Get netcdf dimension
#---------------------------------------------------------------------------
def get_nc_dim(ncin, dimname):
    nc = NetCDFFile(ncin, 'r')
    dim = len(nc.dimensions[dimname])
    nc.close()
    return dim

#---------------------------------------------------------------------------
# Get date of latest plot
#---------------------------------------------------------------------------
def get_latest_plot(plotdir, stns_sail):
    files = glob.glob(plotdir + '/*.png')
    maxdt = -99999
    for f in range(len(files)):
        dt_c = re.findall(r'(\d{10})', files[f])[0]
        if dt_c > maxdt:
            maxdt = dt_c
    return maxdt

#---------------------------------------------------------------------------
# Get obs plot file name.
#---------------------------------------------------------------------------
def get_plotfname(dirin, dtin):
    plotfname = dirin + '/' + dtin + '.png'
    return plotfname

#---------------------------------------------------------------------------
# Get diffs plot file name.
#---------------------------------------------------------------------------
def get_plotfname_diffs(dirin, dtin, model, fhr):
    plotfname = dirin + '/' + model + '_' + dtin + '_f' + fhr + '.png'
    return plotfname

#---------------------------------------------------------------------------
# Get Saildrone netcdf file name
#---------------------------------------------------------------------------
def get_saildrone_fname(dirin, dtin, sdname):
    yyyymmdd = dtin[0:8]
    sdfile = dirin + '/' + yyyymmdd + '/sd.' + sdname + '.' + dtin + '.nc'
    return sdfile

#---------------------------------------------------------------------------
# Get dates for which to make obs plots.
#---------------------------------------------------------------------------
def get_plot_dates(dts, plot_dir, sd_dir, sdnames):
    dts_plot = []
    for d in range(len(dts)):
        dt = dts[d]
        pf = get_plotfname(plot_dir, dt)
        #--- If plot doesn't exist for this date, see if any saildrone data
        #--- exists and if so add this date to our dates to plot.
        if not os.path.isfile(pf):
            found_one = 0
            for s in range(len(sdnames)):
                sd = get_saildrone_fname(sd_dir, dt, sdnames[s])
                if os.path.isfile(sd):
                    found_one = 1
            if found_one == 1:
                dts_plot.append(dt)
    dts_plot = sorted(set(dts_plot), reverse=True)
    return dts_plot

##---------------------------------------------------------------------------
## Get dates for which to make diffs plots.
##---------------------------------------------------------------------------
#def get_diffs_plot_dates(dts, plot_dir, sd_dir, model_data, model, sdnames):
#    dts_plot = []
#    model_files = glob.glob(model_data + '/' + model + '/data/*')
#    for f in range(len(model_files)):
#        dt_c = re.findall(r'(\d{10})', model_files[f])[0]
#        pf = get_plotfname_diffs(plot_dir, dt_c, model, fhr)
#        if not os.path.isfile(pf):
#            found_one = 0
#            for s in range(len(sdnames)):
#                sd = get_saildrone_fname(sd_dir, dt_c, sdnames[s])
#                if os.path.isfile(sd):
#                    found_one = 1
#            if found_one == 1:
#                dts_plot.append(dt_c)
#    dts_plot = sorted(set(dts_plot), reverse=True)
#
#    return dts_plot

#---------------------------------------------------------------------------
# Get dates for which to make diffs plots.
#---------------------------------------------------------------------------
def get_diffs_plot_dates(dts, fhr, plot_dir, sd_dir, model_data, \
                         model, sdnames):
    dts_plot = []
    model_files = glob.glob(model_data + '/' + model + '/data/*')
    for f in range(len(model_files)):
        dt_c = re.findall(r'(\d{10})', model_files[f])[0]
        pf = get_plotfname_diffs(plot_dir, dt_c, model, fhr)
        if not os.path.isfile(pf):
            found_one = 0
            for s in range(len(sdnames)):
                sd = get_saildrone_fname(sd_dir, dt_c, sdnames[s])
                if os.path.isfile(sd):
                    found_one = 1
            if found_one == 1:
                dts_plot.append(dt_c)
    dts_plot = sorted(set(dts_plot), reverse=True)

    return dts_plot

#---------------------------------------------------------------------------
# Temperature and RH to dew point calc.
#---------------------------------------------------------------------------
def relh_to_td(tc, rh):
    a1 = 17.625
    b1 = 243.04
    relh_to_td = (b1 * ( np.log(rh / 100.0) + ((a1 * tc) / (b1 + tc)) )) / \
                 ( a1 - (np.log(rh / 100.0)) - ((a1 * tc) / (b1 + tc)) )
    return relh_to_td

#---------------------------------------------------------------------------
# Load Saildrone netcdf file.
#---------------------------------------------------------------------------
def load_saildrone(sdfile, vars):

    #--- We'll average the last avg_mins minutes of data to get our hourlies.
    avg_mins = 5
    
    nc = NetCDFFile(sdfile, 'r')
    dts  = nc.variables['time'][0,:]
    lats = nc.variables['latitude'][0,:]
    lons = nc.variables['longitude'][0,:]
    lat = np.mean(lats[-avg_mins:])
    lon = np.mean(lons[-avg_mins:])    
                   
    dataout = {}
    dataout['latitude'] = lat
    dataout['longitude'] = lon
    dataout['date']  = unix_to_date(dts[-1], '%Y%m%d%H%M')
    for v in range(len(vars)):
        var = vars[v]
        dat_tmp = nc.variables[var][0,:]

        #--- IR observed sea-surface temperature appears to be observed
        #--- from 28-min before
        #--- the hour through 12-min after the hour on odd numbered hours
        #--- only.  Thus even numbered hours will not have data for the last
        #--- 5-min of the hour.  So average entire hour, figuring sea-surface
        #--- temperature won't vary greatly in an hour compared to other
        #--- variables.
        if var == 'TEMP_IR_SEA_WING_UNCOMP_MEAN':
            dataout[var] = np.mean(dat_tmp)
        else:
            dataout[var] = np.mean(dat_tmp[-avg_mins:])

    td = relh_to_td(dataout['TEMP_AIR_MEAN'], dataout['RH_MEAN'])
    dataout['TD_MEAN'] = td
    
    nc.close()
    return dataout

#---------------------------------------------------------------------------
# Load QC'd rawins file.
#---------------------------------------------------------------------------
def load_qc_rawins(qrfile, rundir):

    grepcom = 'grep -A1 --no-group-separator '
    #--- Grep out ship obs from qc rawins file.
    shipfile = rundir + '/rawins_ship.txt'
    syscom = grepcom + '\"Ship Synoptic\" ' + qrfile + ' > ' + shipfile
    os.system(syscom)

    #--- Grep out buoy obs from qc rawins file.
    buoyfile = rundir + '/rawins_buoy.txt'
    syscom = grepcom + '\"Fixed Buoy\" ' + qrfile + ' > ' + buoyfile
    os.system(syscom)

    #--- cat ship and buoy obs files together.
    obsfile = rundir + '/rawins_obs.txt'
    syscom = 'cat ' + shipfile + ' ' + buoyfile + ' > ' + obsfile
    os.system(syscom)

    #--- Read in ship and buoy obs file.
    f = open(obsfile, 'rb')
    reader = csv.reader(f)
    stns    = []
    typeout = []
    dataout = {}
    line1 = 1
    for line in reader:
        if line1 == 1:
            xlat           = line[0][0:20]
            xlon           = line[0][20:40]
            sn_long        = line[0][40:60]
            typ_desc       = line[0][80:120]
            platform       = line[0][120:160]
            source         = line[0][160:200]
            ter            = line[0][200:220]
            num_valid_flds = line[0][220:230]
            num_errors     = line[0][230:240]
            num_warnings   = line[0][240:250]
            sequence_num   = line[0][250:260]
            num_duplicates = line[0][260:270]
            is_sound       = line[0][270:280]
            bogus          = line[0][280:290]
            discarded      = line[0][290:300]
            i4time         = line[0][300:310]
            julian_day     = line[0][310:320]
            date_char      = line[0][320:340]
            slp            = float(line[0][340:354])
            slpflg         = line[0][355:360]
            pcp6           = line[0][360:374]
            pcp6flg        = line[0][375:381]
            pcp24          = line[0][380:394]
            pcp24flg       = line[0][395:401]

            stn = sn_long.strip()
            stns.append(stn)
            typeout.append(typ_desc.strip())
            dataout[stn,'date'] = date_char.strip()
            dataout[stn,'latitude'] = float(xlat)
            dataout[stn,'longitude'] = float(xlon)

            if slp == mvc_rawins:
                dataout[stn,'slp'] = np.nan
            else:
                dataout[stn,'slp'] = slp
            line1 = 0
        else:
            p       = line[0][0:13]
            pflg    = line[0][15:20]
            z       = line[0][20:33]
            zflg    = line[0][35:40]
            t       = float(line[0][40:53])
            tflg    = line[0][55:60]
            td      = float(line[0][60:73])
            tdflg   = line[0][75:80]
            spd     = float(line[0][80:93])
            spdflg  = line[0][95:100]
            wdir    = float(line[0][100:113])
            wdirflg = line[0][115:120]

            if t == mvc_rawins:
                dataout[stn,'t'] = np.nan
            else:
                dataout[stn,'t'] = t
            if td == mvc_rawins:
                dataout[stn,'td'] = np.nan
            else:
                dataout[stn,'td'] = td
            if spd == mvc_rawins:
                dataout[stn,'spd'] = np.nan
            else:
                dataout[stn,'spd'] = spd
            if wdir == mvc_rawins:
                dataout[stn,'wdir'] = np.nan
            else:
                dataout[stn,'wdir'] = wdir
            
            line1 = 1
    f.close()

    #--- Get u and v from spd and direction.
    for s in range(len(stns)):
        stn = stns[s]
        u, v = dirspd_to_uv(dataout[stn,'wdir'], dataout[stn, 'spd'])
        dataout[stn, 'u'] = u
        dataout[stn, 'v'] = v


    #--- Clean up.
    syscom = 'rm ' + shipfile
    os.system(syscom)
    syscom = 'rm ' + buoyfile
    os.system(syscom)
    syscom = 'rm ' + obsfile
    os.system(syscom)

    return stns, typeout, dataout

