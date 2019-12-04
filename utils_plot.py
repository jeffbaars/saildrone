#!/usr/bin/python
import os, sys, glob, re, math
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm, shiftgrid
from utils_cmap import *
from utils_date import *
from utils_load_data import *
from utils_ghcnd_obs import *
from utils_stats import *

#import cartopy.crs as ccrs
#import cartopy.feature as cfeature

from metpy.calc import reduce_point_density
from metpy.calc import wind_components
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, current_weather, sky_cover, \
     StationPlot, wx_code_map
from metpy.units import units

fs_sail  = 10
fs_sb    = 7
fs       = 9
titlefs  = 10
titlefw  = 'normal'
width    = 7
height   = 7
maplw    = 1.0
ms2knots = 1.94384

col_sail = 'k'
col_ship = 'b'
col_buoy = 'g'

ur_lat =   53.0
ur_lon = -110.0
ll_lat =   27.0
ll_lon = -145.0

var_lab = {
    'TMP_2maboveground'      : '2-m Temperature ($^\circ$F)',
    'DPT_2maboveground'      : '2-m Dew Point Temperature ($^\circ$F)',
    'PRMSL_meansealevel'     : 'Sea Level Pressure (mb)',
    'TMP_surface'            : 'Sea Surface Temperature ($^\circ$F)',
    'WAVE_DOMINANT_PERIOD'   : 'Dominant Wave Period (s)',
    'WAVE_SIGNIFICANT_HEIGHT': 'Significant Wave Height (m)'    
    }
ylims = {
    'TMP_2maboveground'      : [-5, 5],
    'DPT_2maboveground'      : [-5, 5],    
    'PRMSL_meansealevel'     : [-2, 2],
    'TMP_surface'            : [-3, 3],
    'WAVE_DOMINANT_PERIOD'   : [0, 25],
    'WAVE_SIGNIFICANT_HEIGHT': [0, 8]
    }

#---------------------------------------------------------------------------
# Create model-obs diffs time series plot.
#---------------------------------------------------------------------------
def ts_diffs(var, dts, stns_sail, obspts_sail, diffs_sail, modpts_sail, \
             cols, titlein, plotfname):

    fig, ax = plt.subplots( figsize=(7,5) )

    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        diffs_c = []
        xlabs   = []        
        for d in range(len(dts)):
            dt = dts[d]
            key = (stn,dt,var)
            if key in diffs_sail:
                diff_c = diffs_sail[key]
                if var == 'TMP_2maboveground' or \
                   var == 'DPT_2maboveground':
                    diff_c = (diff_c * 9.0/5.0)
                elif var == 'PRMSL_meansealevel':
                    diff_c = diff_c / 100.0
                diffs_c.append(diff_c)
            else:
                diff_c = np.nan
                diffs_c.append(np.nan)
            #print dt, diff_c
            xlabs.append(get_nice_date(dt, dtfmt, dtfmt_nice))
        plt.plot(diffs_c, label = stn, color = cols[s])

    #--- y-axis labeling.
    plt.ylim(ylims[var])
    plt.ylabel(var_lab[var] + ' Differences', fontsize=fs+1)
    plt.tick_params(axis='y', which='major', labelsize=fs+1)    

    #--- x-axis labels.
    xticks_c = range(0,len(xlabs))
    xlabs_c = [ xlabs[i] for i in xticks_c ]    
    plt.xticks(xticks_c)
    plt.tick_params(axis='x', which='major', labelsize=fs-1)
    ax.set_xticklabels(xlabs_c, rotation=90)        
    plt.xlabel('Date', fontsize=fs+1)

    plt.title(titlein, fontsize=titlefs, fontweight='bold')

    plt.tight_layout()
    plt.grid()
    plt.legend(fontsize = fs, loc = 'best')

    print 'xli ', plotfname, ' &'
    plt.savefig(plotfname)
    plt.close()

    return 1

#---------------------------------------------------------------------------
# Create model-obs diffs time series plot.
#---------------------------------------------------------------------------
def ts_obs_ocean(var, dts, stns_sail, obspts_sail, cols, titlein, plotfname):

    xtick_hh_modulus = 6  # put a xtick and label every xtick_hh_modulus hours.
    fig, ax = plt.subplots( figsize=(7,5) )
    xlabs_c  = []
    xticks_c = []
    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        obs_c = []
        for d in range(len(dts)):
            dt = dts[d]
            hh = dt[8:10]
            if s == 0:
                if int(hh) % xtick_hh_modulus == 0:
                    xticks_c.append(d)
                    xlabs_c.append(get_nice_date(dt, dtfmt, dtfmt_nice))
            key = (stn,dt)
            if key in obspts_sail:
                if obspts_sail[key] == obspts_sail[key]:
                    ob_c = obspts_sail[key][var]
                    obs_c.append(ob_c)
                else:
                    obs_c.append(np.nan)                    
            else:
                obs_c.append(np.nan)
        plt.plot(obs_c, label = stn, color = cols[s])

    #--- y-axis labeling.
    plt.ylim(ylims[var])
    plt.ylabel(var_lab[var], fontsize=fs+1)
    plt.tick_params(axis='y', which='major', labelsize=fs+1)    

    #--- x-axis labels.
    plt.xticks(xticks_c)
    plt.tick_params(axis='x', which='major', labelsize=fs-1)
    ax.set_xticklabels(xlabs_c, rotation=90)        
    plt.xlabel('Date', fontsize=fs+1)

    plt.title(titlein, fontsize=titlefs, fontweight='bold')

    plt.tight_layout()
    plt.grid()
    plt.legend(fontsize = fs, loc = 'best')

    print 'xli ', plotfname, ' &'
    plt.savefig(plotfname)
    plt.close()

    return 1

#---------------------------------------------------------------------------
# Create Saildrone, ship and buoy weather station plot map.
#---------------------------------------------------------------------------
def mapper(stns_sail, dat_sail, stns_sb, typ_sb, dat_sb, titlein, plotfname):

    lat_ctr = ll_lat + ((ur_lat - ll_lat) * 0.5)
    lon_ctr = ll_lon + ((ur_lon - ll_lon) * 0.5)

    res = 'l'
        
    fig = plt.figure(figsize=(width,height))
    # left, bottom, width, height:
    ax = fig.add_axes([0.00,0.05,0.99,0.91])
    map = Basemap(resolution = res,projection='lcc',\
                  llcrnrlon= ll_lon, llcrnrlat=ll_lat,\
                  urcrnrlon= ur_lon, urcrnrlat= ur_lat,\
                  lat_0=lat_ctr,lon_0=lon_ctr,lat_1=(ur_lat - ll_lat))

    #--- Draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth = maplw)
    map.drawstates(linewidth = maplw)
    map.drawcountries(linewidth = maplw)
    #map.fillcontinents(color='lightgray')
    
    #--- Draw lat/lon grid lines every 30 degrees.
    map.drawmeridians(np.arange(0, 360, 10), linewidth = maplw)
    map.drawparallels(np.arange(-90, 90, 10), linewidth = maplw)
                   
    #--- Plot Saildrone data.
    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        if dat_sail[stn] != dat_sail[stn]:
            print 'skipping plotting of Saildrone station ', stn
            continue
        else:
            xs,ys = map(dat_sail[stn]['longitude'], dat_sail[stn]['latitude'])

        stationplot = StationPlot(ax, xs, ys, fontsize=fs_sail, color=col_sail)

        temp_c = (dat_sail[stn]['TEMP_AIR_MEAN'] * 9.0/5.0) + 32
        stationplot.plot_parameter('W', [temp_c], color=col_sail)
        td_c = (dat_sail[stn]['TD_MEAN'] * 9.0/5.0) + 32
        stationplot.plot_parameter('SW', [td_c], color=col_sail)

        sst_c = (dat_sail[stn]['TEMP_O2_RBR_MEAN'] * 9.0/5.0) + 32
        stationplot.plot_parameter('SE', [sst_c], color=col_sail)

        # Add wind barbs
        us = dat_sail[stn]['UWND_MEAN'] * ms2knots
        vs = dat_sail[stn]['VWND_MEAN'] * ms2knots
        stationplot.plot_barb([us], [vs], linewidth = 1.5)

        pres_c = dat_sail[stn]['BARO_PRES_MEAN']
        stationplot.plot_parameter('E', [pres_c], formatter = \
                                   lambda v: format(10 * v, '.0f')[-3:])
#        stationplot.plot_text((2, 0), [stn])

    #--- Plot ship and buoy data.
    for s in range(len(stns_sb)):
        stn = stns_sb[s]
        lat = dat_sb[stn,'latitude']
        lon = dat_sb[stn,'longitude']
        t = ((dat_sb[stn,'t']-273.15) * 9.0/5.0) + 32
        td = ((dat_sb[stn,'td']-273.15) * 9.0/5.0) + 32
        spd = dat_sb[stn,'spd'] * ms2knots
        wdir = dat_sb[stn,'wdir']
        u, v = dirspd_to_uv(wdir, spd)
        pres = dat_sb[stn,'slp'] / 100.0
        if np.isnan(t) and np.isnan(td) and np.isnan(u) and np.isnan(pres):
            continue

        #--- Skip obs that'll clutter our title.
        if lat >= ur_lat:
            continue

        #--- Different color for ship and buoy.
        typ = typ_sb[s]
        if re.search('Buoy', typ):
            col = col_buoy
        elif re.search('Ship', typ):
            col = col_ship

        xs, ys = map(lon, lat)
        stationplot = StationPlot(ax, xs, ys, fontsize=fs_sb, color=col)
        stationplot.plot_parameter('W', [t], color=col)
        stationplot.plot_parameter('SW', [td], color=col)
        stationplot.plot_barb([u], [v])
        stationplot.plot_parameter('E', [pres], formatter = \
                                   lambda v: format(10 * v, '.0f')[-3:])
        #stationplot.plot_text((2, 0), [stn])
        
    plt.title(titlein, fontsize=titlefs, fontweight=titlefw)

    #--- Save plot.
    print 'xli ', plotfname, ' &'
    plt.savefig(plotfname)

    plt.close()

    return 1

#---------------------------------------------------------------------------
# Create Saildrone, ship and buoy weather station plot map.
#---------------------------------------------------------------------------
def mapper_diffs(stns_sail, obspts_sail, diffs_sail, modpts_sail, \
                 stns_sb, typ_sb, \
                 obspts_sb, diffs_sb, modpts_sb, grid_model, lat, lon, \
                 titlein, plotfname):

    lat_ctr = ll_lat + ((ur_lat - ll_lat) * 0.5)
    lon_ctr = ll_lon + ((ur_lon - ll_lon) * 0.5)

    res = 'l'
        
    fig = plt.figure(figsize=(width,height))
    # left, bottom, width, height:
    ax = fig.add_axes([0.00,0.05,0.99,0.91])
    map = Basemap(resolution = res,projection='lcc',\
                  llcrnrlon= ll_lon, llcrnrlat=ll_lat,\
                  urcrnrlon= ur_lon, urcrnrlat= ur_lat,\
                  lat_0=lat_ctr,lon_0=lon_ctr,lat_1=(ur_lat - ll_lat))

    #--- Draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth = maplw)
    map.drawstates(linewidth = maplw)
    map.drawcountries(linewidth = maplw)

    #--- Draw lat/lon grid lines every 30 degrees.
    map.drawmeridians(np.arange(0, 360, 10), linewidth = maplw)
    map.drawparallels(np.arange(-90, 90, 10), linewidth = maplw)

    #--- Get slice of grid to contour since contouring entire planet's worth
    #--- causes strange matplotlib behavior.
    grid = np.divide(grid_model['PRMSL_meansealevel'], 100)
    fudge = 6.0
    minj = np.min(np.where(lat[0,:] >= ll_lat - fudge))
    maxj = np.max(np.where(lat[0,:] <= ur_lat + fudge))
    mini = np.min(np.where(lon[:,0] >= (ll_lon - fudge + 360)))
    maxi = np.max(np.where(lon[:,0] <= (ur_lon + fudge + 360)))
    lat_plot = lat[mini:maxi, minj:maxj]
    lon_plot = lon[mini:maxi, minj:maxj]
    grid_plot = grid[mini:maxi, minj:maxj]
    
    x,y = map(lon_plot, lat_plot)

    levs = range(900, 1080, 4)
    cs = plt.contour(x, y, grid_plot, levs, colors='darkgray')
    plt.clabel(cs, cs.levels, fmt='%4.0f')

    #--- Plot Saildrone data.
    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        xs,ys = map(diffs_sail[stn,'longitude'], diffs_sail[stn,'latitude'])
        stationplot = StationPlot(ax, xs, ys, fontsize=fs_sail, color=col_sail)

        temp_c = (diffs_sail[stn,'TMP_2maboveground'] * 9.0/5.0)
        stationplot.plot_parameter('W', [temp_c], color=col_sail, \
                                   formatter='3.1f')
        td_c = (diffs_sail[stn,'DPT_2maboveground'] * 9.0/5.0)
        stationplot.plot_parameter('SW', [td_c], color=col_sail, \
                                   formatter='3.1f')
        sst_c = (diffs_sail[stn,'TMP_surface'] * 9.0/5.0)
        stationplot.plot_parameter('SE', [sst_c], color=col_sail, \
                                   formatter='3.1f')

        pres_c = diffs_sail[stn,'PRMSL_meansealevel'] / 100.0
        stationplot.plot_parameter('E', [pres_c], color=col_sail, \
                                   formatter = '3.1f', fontweight='bold', \
                                   fontsize=fs_sail+1)

        # Add wind barbs, observed.
        us = obspts_sail[stn]['UWND_MEAN'] * ms2knots
        vs = obspts_sail[stn]['VWND_MEAN'] * ms2knots
        stationplot.plot_barb([us], [vs], linewidth = 1.5)

        # Add wind barbs, model.  Have to redraw a StationPlot to do this.
        stationplot = StationPlot(ax, xs, ys, fontsize = fs_sail,color=col_sail)
        us = modpts_sail[stn,'UGRD_10maboveground'] * ms2knots
        vs = modpts_sail[stn,'VGRD_10maboveground'] * ms2knots
        stationplot.plot_barb([us], [vs], linewidth = 1.0, color='r')

        #stationplot.plot_text((2, 0), [stn])

    #--- Plot ship and buoy data.
    for s in range(len(stns_sb)):
        stn = stns_sb[s]
        lat = diffs_sb[stn,'latitude']
        lon = diffs_sb[stn,'longitude']
        t = ((diffs_sb[stn,'TMP_2maboveground']) * 9.0/5.0)
        td = ((diffs_sb[stn,'DPT_2maboveground']) * 9.0/5.0)
        u = obspts_sb[stn,'u']
        v = obspts_sb[stn,'v']        
        pres = diffs_sb[stn,'PRMSL_meansealevel'] / 100.0 # to kPa...
        if np.isnan(t) and np.isnan(td) and np.isnan(u) and np.isnan(pres):
            continue

        #--- Skip obs that'll clutter our title.
        if lat >= ur_lat or lat <= ll_lat:
            continue

        #--- Different color for ship and buoy.
        typ = typ_sb[s]
        if re.search('Buoy', typ):
            col = col_buoy
        elif re.search('Ship', typ):
            col = col_ship

        xs, ys = map(lon, lat)
        stationplot = StationPlot(ax, xs, ys, fontsize=fs_sb, color=col)
        stationplot.plot_parameter('W', [t], color=col)
        stationplot.plot_parameter('SW', [td], color=col)
        stationplot.plot_parameter('E', [pres], color=col, \
                                   fontweight='bold', fontsize=fs_sb+1)

        # Add wind barbs, observed.
        us = obspts_sb[stn,'u'] * ms2knots
        vs = obspts_sb[stn,'v'] * ms2knots
        stationplot.plot_barb([us], [vs])

        # Add wind barbs, model.  Have to redraw a StationPlot to do this.
        stationplot = StationPlot(ax, xs, ys, fontsize = fs_sb, color='r')
        us = modpts_sb[stn,'UGRD_10maboveground'] * ms2knots
        vs = modpts_sb[stn,'VGRD_10maboveground'] * ms2knots
        stationplot.plot_barb([us], [vs], color='r')

        #stationplot.plot_text((2, 0), [stn])
       
    plt.title(titlein, fontsize=titlefs, fontweight=titlefw)

    plt.legend()

    #--- Save plot.
    print 'xli ', plotfname, ' &'
    plt.savefig(plotfname)

    plt.close()

    return 1
