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
#from utils_ghcnd_obs import *
#from utils_stats import *

#---------------------------------------------------------------------------
# Paths.
#---------------------------------------------------------------------------
sail_dir   = '/home/disk/spock/jbaars/saildrone'
py_dir     = sail_dir + '/python'
plot_dir   = sail_dir + '/plots'
pickle_dir = sail_dir + '/pickle'
data_dir   = sail_dir + '/data'

#---------------------------------------------------------------------------
# Settings.
#---------------------------------------------------------------------------
domain = 'd01'
hh     = '00'
geo_em = data_dir + '/geo_em.' + domain + '.nc'

zoom = 'Z1'

plotfname = plot_dir + '/' + 'test.png'

sd_names = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
sd_lats = [47.5, 45.0, 42.5, 40.0, 37.5, 35.0]
sd_lons = [-130.5, -130.5, -130.5, -130.0, -129.0, -127.5]

#---------------------------------------------------------------------------
# Load corner lats/lons from geo_em.
#---------------------------------------------------------------------------
nc = NetCDFFile(geo_em, 'r')
clats_d1 = nc.corner_lats
clons_d1 = nc.corner_lons
nc.close()
(lat, lon, hgt) = load_geo_em(geo_em)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
target_lat = 47.44472
target_lon = -122.31361
fudge_lat = 1.7
fudge_lon = 2.1
minlatZ2 = target_lat - fudge_lat
maxlatZ2 = target_lat + fudge_lat
minlonZ2 = target_lon - fudge_lon
maxlonZ2 = target_lon + fudge_lon
minlat = {
    'Z1': 39.0,
    'Z2': minlatZ2 }
maxlat = {
    'Z1': 51.0,
    'Z2': maxlatZ2 }
minlon = {
    'Z1': -131.0,
    'Z2': minlonZ2 }
maxlon = {
    'Z1': -108.0,
    'Z2': maxlonZ2 }

fs      = 9
titlefs = 9
width   = 10
height  = 8
maplw   = 1.0

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
titlein = 'test'

ur_lat = clats_d1[2]
ur_lon = clons_d1[2]
ll_lat = clats_d1[0] 
ll_lon = clons_d1[0]
    
lat_ctr = clats_d1[0] + ((clats_d1[2] - clats_d1[0]) * 0.5)
lon_ctr = clons_d1[0] + ((clons_d1[2] - clons_d1[0]) * 0.5)

#if (zoom == 'Z1' or zoom == 'Z0'):
#    res = 'i'
#elif (zoom == 'Z2'):
#    res = 'h'

res = 'l'
        
fig = plt.figure(figsize=(width,height))
# left, bottom, width, height:
ax = fig.add_axes([0.00,0.05,0.99,0.91])
map = Basemap(resolution = res,projection='lcc',\
              llcrnrlon= ll_lon, llcrnrlat=ll_lat,\
              urcrnrlon= ur_lon, urcrnrlat= ur_lat,\
              lat_0=lat_ctr,lon_0=lon_ctr,lat_1=(ur_lat - ll_lat))

#--- Get lat and lon data in map's x/y coordinates.
x,y = map(lon, lat)

#--- Draw coastlines, country boundaries, fill continents.
map.drawcoastlines(linewidth = maplw)
map.drawstates(linewidth = maplw)
map.drawcountries(linewidth = maplw)

#--- Draw the edge of the map projection region (the projection limb)
#map.drawmapboundary(linewidth = maplw)

#--- Draw lat/lon grid lines every 30 degrees.
map.drawmeridians(np.arange(0, 360, 30), linewidth = maplw)
map.drawparallels(np.arange(-90, 90, 30), linewidth = maplw)

#--- Plot saildrone locations.
for s in range(len(sd_names)):
    xc,yc = map(sd_lons[s], sd_lats[s])
    plt.plot(xc, yc, 'o')
    plt.text(xc, yc, sd_names[s])

plt.title(titlein, fontsize=titlefs, fontweight='bold')

#--- Save plot.
print 'xli ', plotfname, ' &'
plt.savefig(plotfname)

plt.close()

